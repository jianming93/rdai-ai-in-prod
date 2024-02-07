import logging

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)
import json
import sys

import numpy as np
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import InferenceServerException

#!/usr/bin/env python3

# Copyright 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import asyncio
import json
import sys

import numpy as np
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import *


class LLMClient:
    def __init__(
        self,
        triton_server_url,
        triton_server_port,
        triton_server_model_name,
        triton_server_verbose,
        streaming_mode=False,
        stream_timeout=10,
    ):
        self.triton_server_url = triton_server_url
        self.triton_server_port = triton_server_port
        self.triton_server_model_name = triton_server_model_name
        self.triton_server_verbose = triton_server_verbose
        self.streaming_mode = streaming_mode
        self.stream_timeout = float(stream_timeout)
        self._client = grpcclient.InferenceServerClient(
            url=f"{triton_server_url}:{triton_server_port}",
            verbose=triton_server_verbose,
        )
        self._loop = asyncio.get_event_loop()
        self._results_dict = {}
        self.offset = 0

    async def async_request_iterator(self, prompts, sampling_parameters):
        try:
            for i, prompt in enumerate(prompts):
                prompt_id = self.offset + i
                self._results_dict[str(prompt_id)] = []
                yield self.create_request(
                    prompt,
                    self.streaming_mode,
                    prompt_id,
                    sampling_parameters,
                )
        except Exception as error:
            logging.error(f"Caught an error in the request iterator: {error}")

    async def stream_infer(self, prompts, sampling_parameters):
        try:
            # Start streaming
            response_iterator = self._client.stream_infer(
                inputs_iterator=self.async_request_iterator(
                    prompts, sampling_parameters
                ),
                stream_timeout=self.stream_timeout,
            )
            async for response in response_iterator:
                yield response
        except InferenceServerException as error:
            logging.error(error)
            sys.exit(1)

    async def process_stream(self, prompts, sampling_parameters):
        # Clear results in between process_stream calls
        self.results_dict = []

        # Read response from the stream
        async for response in self.stream_infer(prompts, sampling_parameters):
            result, error = response
            if error:
                logging.error(f"Encountered error while processing: {error}")
            else:
                output = result.as_numpy("text_output")
                for i in output:
                    self._results_dict[result.get_response().id].append(i)

    async def run(self, prompts, sampling_parameters):
        await self.process_stream(prompts, sampling_parameters)

        output = self._results_dict["0"][-1].decode()

        if self.triton_server_verbose:
            logging.info("Generated output: %s" % output)

        return output

    def create_request(
        self,
        prompt,
        stream,
        request_id,
        sampling_parameters,
        send_parameters_as_tensor=True,
    ):
        inputs = []
        prompt_data = np.array([prompt.encode("utf-8")], dtype=np.object_)
        try:
            inputs.append(grpcclient.InferInput("text_input", [1], "BYTES"))
            inputs[-1].set_data_from_numpy(prompt_data)
        except Exception as error:
            logging.error(f"Encountered an error during request creation: {error}")

        stream_data = np.array([stream], dtype=bool)
        inputs.append(grpcclient.InferInput("stream", [1], "BOOL"))
        inputs[-1].set_data_from_numpy(stream_data)

        # Request parameters are not yet supported via BLS. Provide an
        # optional mechanism to send serialized parameters as an input
        # tensor until support is added

        if send_parameters_as_tensor:
            sampling_parameters_data = np.array(
                [json.dumps(sampling_parameters).encode("utf-8")], dtype=np.object_
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
            "parameters": sampling_parameters,
        }
