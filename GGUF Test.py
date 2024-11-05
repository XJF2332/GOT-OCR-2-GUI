import ctypes
from llama_cpp import Llama, StoppingCriteriaList
import llama_cpp.llava_cpp as llava_cpp
import llama_cpp.llava_cpp
import torch


def float_list_to_ctypes_array(float_list):
    # 创建一个ctypes的float数组类型
    FloatArray = ctypes.c_float * len(float_list)

    # 使用这个类型创建一个新的ctypes数组，并用float_list初始化它
    return FloatArray(*float_list)


llm = Llama(
    model_path=r"gguf\None-464M-123-F16.gguf",
    n_gpu_layers=-1, # Uncomment to use GPU acceleration
    n_ctx=2048,  # Uncomment to increase the context window
    n_batch=1024
)

n_past = ctypes.c_int(llm.n_tokens)
n_past_p = ctypes.pointer(n_past)

tensor = torch.load('tensor.pt')
print(tensor.shape)

# 将张量转换为 NumPy 数组
embd_image = tensor.numpy().reshape(-1).tolist()
c_float_array = float_list_to_ctypes_array(embd_image)
embed = llava_cpp.llava_image_embed(embed=c_float_array, n_image_pos=286)

with llama_cpp.suppress_stdout_stderr(disable=True):
    aa = llava_cpp.llava_eval_image_embed(
        llm.ctx,
        embed,
        llm.n_batch,
        n_past_p,
    )
    print(f"aa:{aa},n_past_p:{n_past.value}")
# Required to avoid issues with hf tokenizer
# llm.input_ids[llm.n_tokens : n_past.value] = -1
llm.n_tokens = n_past.value
# Get prompt tokens to avoid a cache miss
prompt = llm.input_ids[: llm.n_tokens].tolist()

token_ids = {
    # add the end of text token
    llm.detokenize([llm._token_eos]),
    int(151645),
}


def stop_on_token_ids(tokens, *args, **kwargs):
    return tokens[-1] in token_ids


stopping_criteria = StoppingCriteriaList([stop_on_token_ids])

for token in llm.generate(prompt, stopping_criteria=stopping_criteria):
    print(llm.detokenize([token]).decode(errors="ignore"), end="")

output = llm(
      prompt, # Prompt
      max_tokens=3032, # Generate up to 32 tokens, set to None to generate up to the end of the context window
      stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      echo=True # Echo the prompt back in the output
) # Generate a completion, can also call create_completion
print(output["choices"][0]["text"])