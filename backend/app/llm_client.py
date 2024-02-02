import logging
logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
import json
import sys

import numpy as np
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import InferenceServerException


class LLMClient:
    def __init__(
        self,
        triton_server_url,
        triton_server_port,
        triton_server_model_name,
        triton_server_verbose,
        streaming_mode=False,
        stream_timeout=10,
        temperature=0.1,
        top_p=0.95
    ):
        self.triton_server_url = triton_server_url
        self.triton_server_port = triton_server_port
        self.triton_server_model_name = triton_server_model_name
        self.triton_server_verbose = triton_server_verbose
        self.streaming_mode = streaming_mode
        self.stream_timeout = stream_timeout
        self.temperature = temperature
        self.top_p = top_p
        self._client = grpcclient.InferenceServerClient(
            url=f"{triton_server_port}:{triton_server_port}",
            verbose=triton_server_verbose
        )
        self._results_dict = {}
        self.prompt_id = 1
        self.sampling_parameters = {
            "temperature": temperature,
            "top_p": top_p
        }

    async def async_request_iterator(self, prompts):
        try:
            for prompt in prompts:
                self._results_dict[str(self.prompt_id)] = []
                yield self.create_request(
                    prompt,
                    self.streaming_mode,
                    self.prompt_id,
                )
                self.prompt_id += 1
        except Exception as error:
            logging.error(f"Caught an error in the request iterator: {error}")

    async def stream_infer(self, prompts):
        try:
            # Start streaming
            response_iterator = self._client.stream_infer(
                inputs_iterator=self.async_request_iterator(
                    prompts
                ),
                stream_timeout=float(self.stream_timeout),
            )
            async for response in response_iterator:
                yield response
        except InferenceServerException as error:
            logging.exception(error)
            sys.exit(1)

    async def process_stream(self, prompts):
        # Clear results in between process_stream calls
        self.results_dict = []

        # Read response from the stream
        async for response in self.stream_infer(prompts):
            result, error = response
            if error:
                logging.error(f"Encountered error while processing: {error}")
            else:
                output = result.as_numpy("text_output")
                for i in output:
                    self._results_dict[result.get_response().id].append(i)

    async def run(self, prompts):
        await self.process_stream(prompts)

    def create_request(
        self,
        prompt,
        stream,
        request_id,
        send_parameters_as_tensor=True,
    ):
        inputs = []
        # Set prompt
        prompt_data = np.array([prompt.encode("utf-8")], dtype=np.object_)
        try:
            inputs.append(grpcclient.InferInput("text_input", [1], "BYTES"))
            inputs[-1].set_data_from_numpy(prompt_data)
        except Exception as error:
            logging.error(f"Encountered an error during request creation: {error}")
        # Set stream
        stream_data = np.array([stream], dtype=bool)
        inputs.append(grpcclient.InferInput("stream", [1], "BOOL"))
        inputs[-1].set_data_from_numpy(stream_data)

        # Request parameters are not yet supported via BLS. Provide an
        # optional mechanism to send serialized parameters as an input
        # tensor until support is added
        # Set sampling params
        if send_parameters_as_tensor:
            sampling_parameters_data = np.array(
                [json.dumps(self.sampling_parameters).encode("utf-8")], dtype=np.object_
            )
            inputs.append(grpcclient.InferInput("sampling_parameters", [1], "BYTES"))
            inputs[-1].set_data_from_numpy(sampling_parameters_data)

        # Add requested outputs
        outputs = []
        outputs.append(grpcclient.InferRequestedOutput("text_output"))

        # Issue the asynchronous sequence inference.
        return {
            "model_name": self.triton_server_model_name,
            "inputs": inputs,
            "outputs": outputs,
            "request_id": str(request_id),
            "parameters": self.sampling_parameters,
        }
