import split_text_chunks as stc

def test_get_embedding_calls_ollama(monkeypatch):
    called = {}
    def fake_get_ollama_embedding(text, model_name, ollama_url):
        called['called'] = True
        assert text == 'hello'
        assert model_name == 'model'
        assert ollama_url == stc.OLLAMA_URL
        return [0.1, 0.2]
    monkeypatch.setattr(stc, 'get_ollama_embedding', fake_get_ollama_embedding)
    result = stc.get_embedding('hello', embedding_type='ollama', model_name='model')
    assert called.get('called', False), 'get_ollama_embedding was not called'
    assert result == [0.1, 0.2]
