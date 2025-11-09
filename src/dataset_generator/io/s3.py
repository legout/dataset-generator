from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import fsspec


@dataclass(frozen=True)
class S3Config:
    uri: str
    key: str
    secret: str
    endpoint_url: Optional[str] = None
    region: str = "us-east-1"
    use_ssl: Optional[bool] = None
    extra_client_kwargs: Optional[Dict[str, Any]] = None

    def to_fsspec_kwargs(self) -> Dict[str, Any]:
        client_kwargs: Dict[str, Any] = {"region_name": self.region}
        if self.endpoint_url:
            client_kwargs["endpoint_url"] = self.endpoint_url
            if self.use_ssl is not None:
                client_kwargs["use_ssl"] = self.use_ssl
            elif self.endpoint_url.startswith("http://"):
                client_kwargs["use_ssl"] = False
        if self.extra_client_kwargs:
            client_kwargs.update(self.extra_client_kwargs)

        return {
            "key": self.key,
            "secret": self.secret,
            "client_kwargs": client_kwargs,
        }


def filesystem_and_root(output: str, s3: S3Config | None) -> Tuple[fsspec.AbstractFileSystem, str]:
    if not output:
        raise ValueError("'output' must be a non-empty path or URI")

    if s3:
        fs = fsspec.filesystem("s3", **s3.to_fsspec_kwargs())
        root = s3.uri.rstrip("/")
        if output != ".":
            root = f"{root}/{output.strip('/')}"
        return fs, root

    os.makedirs(output, exist_ok=True)
    return fsspec.filesystem("file"), os.path.abspath(output)
