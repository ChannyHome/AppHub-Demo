import enum
from sqlalchemy import (
    String, BigInteger, Integer, DateTime, ForeignKey, Text,
    Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class AppKind(str, enum.Enum):
    native = "native"
    web = "web"

class PackageType(str, enum.Enum):
    zip = "zip"
    msi = "msi"
    exe = "exe"

class StorageType(str, enum.Enum):
    ftp = "ftp"
    local = "local"

class AppCategory(Base):
    __tablename__ = "app_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_categories.id"), nullable=False)
    app_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    icon: Mapped[str | None] = mapped_column(String(512), nullable=True)
    manual: Mapped[str | None] = mapped_column(String(512), nullable=True)
    voc: Mapped[str | None] = mapped_column(String(512), nullable=True)

    app_kind: Mapped[AppKind] = mapped_column(SAEnum(AppKind), nullable=False)
    web_launch_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    requires_app_approval: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    latest_version_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # MVP: FK 없음

    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class AppVersion(Base):
    __tablename__ = "app_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    app_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("apps.id"), nullable=False)

    version: Mapped[str] = mapped_column(String(40), nullable=False)
    release_note_short: Mapped[str | None] = mapped_column(String(400), nullable=True)
    release_note_long: Mapped[str | None] = mapped_column(Text, nullable=True)  # MEDIUMTEXT OK
    released_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)

    released_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class AppArtifact(Base):
    __tablename__ = "app_artifacts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    app_version_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_versions.id"), nullable=False)

    os: Mapped[str] = mapped_column(String(20), nullable=False, default="windows")
    arch: Mapped[str] = mapped_column(String(20), nullable=False, default="x86")

    package_type: Mapped[PackageType] = mapped_column(SAEnum(PackageType), nullable=False)
    storage_type: Mapped[StorageType] = mapped_column(SAEnum(StorageType), nullable=False)

    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
