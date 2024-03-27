from langchain_openai import ChatOpenAI, OpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import StrOutputParser
import pytest
import types
from langfuse.callback import CallbackHandler
from tests.utils import get_api
from .utils import create_uuid


# to avoid the instanciation of langfuse in side langfuse.openai.
def _is_streaming_response(response):
    return isinstance(response, types.GeneratorType) or isinstance(
        response, types.AsyncGeneratorType
    )


# Streaming in chat models
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4"])
def test_stream_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(streaming=True, max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    res = model.stream(
        [{"role": "user", "content": "return the exact phrase - This is a test!"}],
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    for chunk in res:
        print(chunk.content, end="", flush=True)
        response_str.append(chunk.content)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Streaming in completions models
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
def test_stream_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(streaming=True, max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    res = model.stream(
        "return the exact phrase - This is a test!",
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    for chunk in res:
        print(chunk, end="", flush=True)
        response_str.append(chunk)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == "gpt-3.5-turbo-instruct"
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Invoke in chat models
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4"])
def test_invoke_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    _ = model.invoke(
        [{"role": "user", "content": "return the exact phrase - This is a test!"}],
        config={"callbacks": [callback]},
    )

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Invoke in completions models
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
def test_invoke_in_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    test_phrase = "This is a test!"
    res = model.invoke(
        f"return the exact phrase - {test_phrase}",
        config={"callbacks": [callback]},
    )

    print(res)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == "gpt-3.5-turbo-instruct"
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert test_phrase in generation.output
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async stream in chat models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4"])
async def test_astream_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(streaming=True, max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    res = model.astream(
        [{"role": "user", "content": "Who was the first American president "}],
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    async for chunk in res:
        print(chunk.content, end="", flush=True)
        response_str.append(chunk.content)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 1
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async stream in completions model
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
async def test_astream_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(streaming=True, max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    test_phrase = "This is a test!"
    res = model.astream(
        f"return the exact phrase - {test_phrase}",
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    async for chunk in res:
        print(chunk, end="", flush=True)
        response_str.append(chunk)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 1
    assert test_phrase in "".join(response_str)
    assert generation.model == "gpt-3.5-turbo-instruct"
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert test_phrase in generation.output
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async invoke in chat models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4"])
async def test_ainvoke_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    test_phrase = "This is a test!"
    _ = await model.ainvoke(
        [{"role": "user", "content": f"return the exact phrase - {test_phrase} "}],
        config={"callbacks": [callback]},
    )

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
async def test_ainvoke_in_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    test_phrase = "This is a test!"
    res = await model.ainvoke(
        f"return the exact phrase - {test_phrase}",
        config={"callbacks": [callback]},
    )

    print(res)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(trace.observations) == 1
    assert trace.name == name
    assert generation.model == "gpt-3.5-turbo-instruct"
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert generation.metadata["tags"] == tags
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert test_phrase in generation.output
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Chains


# Async invoke in chains and chat models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo"])
async def test_chains_ainvoke_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    prompt1 = ChatPromptTemplate.from_template(
        """You are a skilled writer tasked with crafting an engaging introduction for a blog post on the following topic:
        Topic: {topic}
        Introduction: This is an engaging introduction for the blog post on the topic above:"""
    )
    chain = prompt1 | model | StrOutputParser()
    res = chain.invoke(
        {"topic": "The Impact of Climate Change"},
        config={"callbacks": [callback]},
    )

    print(res)
    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    print(generationList)

    generation = generationList[0]

    assert len(trace.observations) == 4
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert all(x in generation.metadata["tags"] for x in tags)
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async invoke in chains and completions models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
async def test_chains_ainvoke_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    prompt1 = PromptTemplate.from_template(
        """You are a skilled writer tasked with crafting an engaging introduction for a blog post on the following topic:
        Topic: {topic}
        Introduction: This is an engaging introduction for the blog post on the topic above:"""
    )
    chain = prompt1 | model | StrOutputParser()
    res = chain.invoke(
        {"topic": "The Impact of Climate Change"},
        config={"callbacks": [callback]},
    )

    print(res)
    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    print(generationList)

    generation = generationList[0]

    assert len(trace.observations) == 4
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert all(x in generation.metadata["tags"] for x in tags)
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async streaming in chat models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo", "gpt-4"])
async def test_chains_astream_chat_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = ChatOpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    prompt1 = PromptTemplate.from_template(
        """You are a skilled writer tasked with crafting an engaging introduction for a blog post on the following topic:
        Topic: {topic}
        Introduction: This is an engaging introduction for the blog post on the topic above:"""
    )
    chain = prompt1 | model | StrOutputParser()
    res = chain.astream(
        {"topic": "The Impact of Climate Change"},
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    async for chunk in res:
        print(chunk, end="", flush=True)
        response_str.append(chunk)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 4
    assert trace.name == name
    assert generation.model == model_name
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert all(x in generation.metadata["tags"] for x in tags)
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.output["content"] is not None
    assert generation.output["role"] is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None


# Async Streaming in completions models
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", ["gpt-3.5-turbo-instruct"])
async def test_chains_astream_completions_models(model_name):
    name = create_uuid()
    tags = ["Hello", "world"]
    model = OpenAI(max_tokens=300, tags=tags, model=model_name)
    callback = CallbackHandler(trace_name=name)
    prompt1 = PromptTemplate.from_template(
        """You are a skilled writer tasked with crafting an engaging introduction for a blog post on the following topic:
        Topic: {topic}
        Introduction: This is an engaging introduction for the blog post on the topic above:"""
    )
    chain = prompt1 | model | StrOutputParser()
    res = chain.astream(
        {"topic": "The Impact of Climate Change"},
        config={"callbacks": [callback]},
    )
    response_str = []
    assert _is_streaming_response(res)
    async for chunk in res:
        print(chunk, end="", flush=True)
        response_str.append(chunk)

    callback.flush()
    api = get_api()
    trace = api.trace.get(callback.get_trace_id())
    generationList = list(filter(lambda o: o.type == "GENERATION", trace.observations))
    assert len(generationList) != 0

    generation = generationList[0]

    assert len(response_str) > 1  # To check there are more than one chunk.
    assert len(trace.observations) == 4
    assert trace.name == name
    assert generation.model == "gpt-3.5-turbo-instruct"
    assert generation.input is not None
    assert generation.output is not None
    assert generation.model_parameters.get("max_tokens") is not None
    assert generation.model_parameters.get("temperature") is not None
    assert all(x in generation.metadata["tags"] for x in tags)
    assert generation.usage.output is not None
    assert generation.usage.total is not None
    assert generation.input_price is not None
    assert generation.output_price is not None
    assert generation.calculated_input_cost is not None
    assert generation.calculated_output_cost is not None
    assert generation.calculated_total_cost is not None
    assert generation.latency is not None
