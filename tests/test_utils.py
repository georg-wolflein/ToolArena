import asyncio
from collections.abc import Container, Mapping
from typing import Sequence

import pytest
from toolarena.utils import stream_reader_to_str_stream, substitute_env_vars


@pytest.fixture
def allow_all() -> Container[str]:
    """Fixture that allows all environment variables."""

    class _AllowAll:
        def __contains__(self, item: str) -> bool:
            return True

    return _AllowAll()


@pytest.fixture
def test_env() -> Mapping[str, str]:
    """Fixture providing a test environment with common variables."""
    return {
        "HOME": "/home/user",
        "USER": "john",
        "EMPTY": "",
        "FOO": "bar",
        "BAR": "baz",
    }


@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        ("hello world", "hello world"),  # No substitution needed
        ("${env:HOME}/docs", "/home/user/docs"),  # Single substitution
        ("${env:USER}:${env:HOME}", "john:/home/user"),  # Multiple substitutions
        ("${env:FOO}${env:BAR}", "barbaz"),  # Adjacent substitutions
        ("prefix${env:EMPTY}suffix", "prefixsuffix"),  # Empty value substitution
    ],
    ids=[
        "no_substitution",
        "single_substitution",
        "multiple_substitutions",
        "adjacent_substitutions",
        "empty_substitution",
    ],
)
def test_env_var_substitution(
    input_str: str,
    expected_output: str,
    test_env: Mapping[str, str],
    allow_all: Container[str],
) -> None:
    """Test environment variable substitution in various scenarios."""
    assert (
        substitute_env_vars(input_str, env=test_env, allowed=allow_all)
        == expected_output
    )


def test_missing_env_var(
    test_env: Mapping[str, str], allow_all: Container[str]
) -> None:
    """Test behavior when environment variable is not found."""
    assert (
        substitute_env_vars("${env:NONEXISTENT}", env=test_env, allowed=allow_all)
        == "${env:NONEXISTENT}"
    )


def test_system_env_var(allow_all: Container[str]) -> None:
    """Test that function works with system environment when env=None."""
    import os

    os.environ["TEST_VAR"] = "test_value"
    try:
        assert substitute_env_vars("${env:TEST_VAR}", allowed=allow_all) == "test_value"
    finally:
        del os.environ["TEST_VAR"]


def test_disallowed_env_var(test_env: Mapping[str, str]) -> None:
    """Test that disallowed environment variables are not substituted."""

    class _AllowNone:
        def __contains__(self, item: str) -> bool:
            return False

    assert (
        substitute_env_vars("${env:HOME}", env=test_env, allowed=_AllowNone())
        == "${env:HOME}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_bytes,expected_output,chunk_size",
    [
        (b"", [], 1),
        (b"hello world", ["hello world"], 100),
        (b"hello world", ["hello", " worl", "d"], 5),
        (b"\xe2\x82\xac", ["", "", "€"], 1),
        (b"\xe2\x82\xac20", ["", "", "€", "2", "0"], 1),
    ],
    ids=["empty", "single_chunk", "multiple_chunks", "split_unicode", "unicode"],
)
async def test_stream_reader_to_str_stream(
    input_bytes: bytes, expected_output: Sequence[str], chunk_size: int
) -> None:
    """
    Test the stream_reader_to_str_stream function with various input scenarios.

    Args:
        input_bytes: Bytes to feed into the stream
        expected_output: Expected string chunks from the stream
    """
    # Create a StreamReader
    reader = asyncio.StreamReader()

    # Feed the chunks to the reader
    reader.feed_data(input_bytes)
    reader.feed_eof()

    # Collect the output
    result = [
        chunk
        async for chunk in stream_reader_to_str_stream(reader, chunk_size=chunk_size)
    ]

    assert result == expected_output
