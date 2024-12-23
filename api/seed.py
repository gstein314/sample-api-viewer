import asyncio
import random
from api.database import database, species, organs_tissues, microscope_types, images

# ローカル環境でのデータベース接続
# from database import database, species, organs_tissues, microscope_types, images

# サンプルデータ
SPECIES = ["Mouse", "Rat", "Human", "Arabidopsis", "Tobacco"]
ORGANS_TISSUES = [
    "Brain", "Heart", "Liver", "Kidney", "Ileum", "Spleen", 
    "Pancreas", "Lung", "Skin", "Blood cell", "Root", 
    "Leaf", "Flower", "Seed", "Stem", "Cultured Cell"
]
MICROSCOPE_TYPES = [
    "Light Microscope", "Electron Microscope", 
    "Fluorescence Microscope", "Confocal Microscope"
]

# サンプル画像データを生成する関数
def generate_random_image(species_id, organ_tissue_id, microscope_type_id):
    thumbnail_url = f"https://example.com/images/{species_id}_{organ_tissue_id}_{microscope_type_id}.jpg"
    description = f"Image of {ORGANS_TISSUES[organ_tissue_id - 1]} from {SPECIES[species_id - 1]} captured by {MICROSCOPE_TYPES[microscope_type_id - 1]}"
    em_image_viewer_url = f"https://example.com/viewer/{species_id}_{organ_tissue_id}_{microscope_type_id}"
    image_size = f"{random.randint(1, 10)}MB"

    return {
        "thumbnail": thumbnail_url,
        "description": description,
        "em_image_viewer_url": em_image_viewer_url,
        "image_size": image_size,
        "species_id": species_id,
        "organ_tissue_id": organ_tissue_id,
        "microscope_type_id": microscope_type_id
    }

async def seed_data():
    # データベース接続
    await database.connect()

    # Species データを挿入
    await database.execute_many(query=species.insert(), values=[{"name": name} for name in SPECIES])

    # Organs/Tissues データを挿入
    organ_tissue_values = []
    for species_id in range(1, len(SPECIES) + 1):  # 各 Species に対応
        for organ in ORGANS_TISSUES:
            organ_tissue_values.append({"name": organ, "species_id": species_id})
    await database.execute_many(query=organs_tissues.insert(), values=organ_tissue_values)

    # Microscope Types データを挿入
    await database.execute_many(query=microscope_types.insert(), values=[{"name": name} for name in MICROSCOPE_TYPES])

    # Images データを挿入
    image_values = []
    for species_id in range(1, len(SPECIES) + 1):  # 各 Species に対応
        for organ_tissue_id in range(1, len(ORGANS_TISSUES) + 1):  # 各 Organs/Tissues に対応
            for microscope_type_id in range(1, len(MICROSCOPE_TYPES) + 1):  # 各 Microscope Type に対応
                if random.random() < 0.2:  # ランダムに一部だけ画像を生成
                    image_values.append(
                        generate_random_image(species_id, organ_tissue_id, microscope_type_id)
                    )

    await database.execute_many(query=images.insert(), values=image_values)

    # データベース接続を閉じる
    await database.disconnect()

# 実行
asyncio.run(seed_data())
