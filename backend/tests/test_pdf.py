from app.services.pdf import split_text


def test_recursive_splitter_respects_size_and_overlap():
    chunks = split_text("alpha " * 600, chunk_size=1000, overlap=200)
    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert chunks[0][-20:].strip().split()[0] in chunks[1]
