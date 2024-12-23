from fastapi import FastAPI, HTTPException
from api.database import database, species, organs_tissues, microscope_types, images

app = FastAPI()

# データベース接続イベント
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# API 1: 全ての Species, Organs/Tissues, Microscope Types を返す
@app.get("/api/v1/all_info")
async def get_all_info():
    # Species を全て取得
    all_species = await database.fetch_all(species.select())

    # Organs/Tissues を全て取得
    all_organs_tissues = await database.fetch_all(organs_tissues.select())

    # Microscope Types を全て取得
    all_microscope_types = await database.fetch_all(microscope_types.select())

    return {
        "species": [{"id": s["id"], "name": s["name"]} for s in all_species],
        "organs_tissues": [
            {"id": ot["id"], "name": ot["name"], "species_id": ot["species_id"]}
            for ot in all_organs_tissues
        ],
        "microscope_types": [{"id": mt["id"], "name": mt["name"]} for mt in all_microscope_types],
    }


# API 2: 生物種に対応する Organs/Tissues と Microscope Types を返す
@app.get("/api/v1/info")
async def get_species_info(species_name: str):
    # 指定された Species を取得
    query = species.select().where(species.c.name == species_name)
    species_data = await database.fetch_one(query)
    if not species_data:
        raise HTTPException(status_code=404, detail="Species not found")

    # 対応する Organs/Tissues を取得
    organ_query = organs_tissues.select().where(organs_tissues.c.species_id == species_data["id"])
    organs = await database.fetch_all(organ_query)

    # 全ての Microscope Types を取得
    microscopes = await database.fetch_all(microscope_types.select())

    return {
        "organs_tissues": [organ["name"] for organ in organs],
        "microscope_types": [microscope["name"] for microscope in microscopes]
    }

@app.get("/api/v1/table_data")
async def get_table_data(
    species_name: str = None, 
    organ_tissue: str = None, 
    microscope_type: str = None
):
    # ベースクエリ: images テーブルから全てのデータを選択
    image_query = images.select()

    # Species でフィルタリング
    if species_name:
        species_query = species.select().where(species.c.name == species_name)
        species_data = await database.fetch_one(species_query)
        if not species_data:
            raise HTTPException(status_code=404, detail="Species not found")
        image_query = image_query.where(images.c.species_id == species_data["id"])

    # Organs/Tissues でフィルタリング
    if organ_tissue:
        organ_query = organs_tissues.select().where(organs_tissues.c.name == organ_tissue)
        organ_data = await database.fetch_one(organ_query)
        if not organ_data:
            raise HTTPException(status_code=404, detail="Organ/Tissue not found")
        image_query = image_query.where(images.c.organ_tissue_id == organ_data["id"])

    # Microscope Types でフィルタリング
    if microscope_type:
        microscope_query = microscope_types.select().where(microscope_types.c.name == microscope_type)
        microscope_data = await database.fetch_one(microscope_query)
        if not microscope_data:
            raise HTTPException(status_code=404, detail="Microscope Type not found")
        image_query = image_query.where(images.c.microscope_type_id == microscope_data["id"])

    # フィルタリングされたデータを取得
    filtered_images = await database.fetch_all(image_query)

    # データを詳細形式で整形して返す
    results = []
    for image in filtered_images:
        species_data = await database.fetch_one(species.select().where(species.c.id == image["species_id"]))
        organ_data = await database.fetch_one(organs_tissues.select().where(organs_tissues.c.id == image["organ_tissue_id"]))
        microscope_data = await database.fetch_one(microscope_types.select().where(microscope_types.c.id == image["microscope_type_id"]))

        results.append({
            "thumbnail": image["thumbnail"],
            "id": image["id"],
            "description": image["description"],
            "em_image_viewer_url": image["em_image_viewer_url"],
            "species": species_data["name"],
            "organ_tissue": organ_data["name"],
            "microscope_type": microscope_data["name"],
            "image_size": image["image_size"]
        })

    return {"results": results}
