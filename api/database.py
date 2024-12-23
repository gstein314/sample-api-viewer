from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer, ForeignKey
)
from databases import Database

DATABASE_URL = "sqlite:///./test.db"

# データベース接続
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# テーブル定義
species = Table(
    "species",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True, nullable=False),
)

organs_tissues = Table(
    "organs_tissues",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("species_id", Integer, ForeignKey("species.id"), nullable=False),
)

microscope_types = Table(
    "microscope_types",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

images = Table(
    "images",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("thumbnail", String),
    Column("description", String),
    Column("em_image_viewer_url", String),
    Column("image_size", String),
    Column("species_id", Integer, ForeignKey("species.id"), nullable=False),
    Column("organ_tissue_id", Integer, ForeignKey("organs_tissues.id"), nullable=False),
    Column("microscope_type_id", Integer, ForeignKey("microscope_types.id"), nullable=False),
)

# テーブル作成
metadata.create_all(engine)
