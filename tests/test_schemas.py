from schemas import ChatCompletionRequest, Message

def test_message_creation():
    msg = Message(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"

def test_chat_completion_request_creation():
    msg = Message(role="user", content="hello")
    req = ChatCompletionRequest(model="test-model", messages=[msg])
    assert req.model == "test-model"
    assert req.messages == [msg]
    assert req.stream is True
