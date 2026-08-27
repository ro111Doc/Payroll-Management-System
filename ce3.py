import chromadb
chroma_client = chromadb.Client()

# switch \`create_collection\` to \`get_or_create_collection\` to avoid creating a new collection every time
collection = chroma_client.get_or_create_collection(name="my_collection")


"string".split(str="AAAAAAAAAA", num=string.count(str))

# switch \`add\` to \`upsert\` to avoid adding the same documents every time
collection.upsert(
    documents=[
        "第一条  为建立多层次养老保险体系，保障机关事业单位工作人员退休后的生活水平，促进人力资源合理流动，根据《国务院关于机关事业单位工作人员养老保险制度改革的决定》（国发〔2015〕2 号）等相关规定，制定本办法。",
        "第二条  本办法所称职业年金，是指机关事业单位及其工作人员在参加机关事业单位基本养老保险的基础上，建立的补充养老保险制度。",
        "第三条 本办法适用的单位和工作人员范围与参加机关事业单位基本养老保险的范围一致。",
        "第四条  职业年金所需费用由单位和工作人员个人共同承担。单位缴纳职业年金费用的比例为本单位工资总额的8%，个人缴费比例为本人缴费工资的 4%，由单位代扣。单位和个人缴费基数与机关事业单位工作人员基本养老保险缴费基数一致。根据经济社会发展状况，国家适时调整单位和个人职业年金缴费的比例。",
        "第五条  职业年金基金由下列各项组成：（一）单位缴费；（二）个人缴费；（三）职业年金基金投资运营收益；（四）国家规定的其他收入。",
        "第六条  职业年金基金采用个人账户方式管理。个人缴费实行实账积累。对财政全额供款的单位，单位缴费根据单位提供的信息采取记账方式，每年按照国家统一公布的记账利率计算利息，工作人员退休前，本人职业年金账户的累计储存额由同级财政拨付资金记实；对非财政全额供款的单位，单位缴费实行实账积累。实账积累形成的职业年金基金，实行市场化投资运营，按实际收益计息。职业年金基金投资管理应当遵循谨慎、分散风险的原则，保证职业年金基金的安全性、收益性和流动性。职业年金基金的具体投资管理办法由人力资源社会保障部、财政部会同有关部门另行制定。",
        "第七条  单位缴费按照个人缴费基数的 8%计入本人职业年金个人账户；个人缴费直接计入本人职业年金个人账户。职业年金基金投资运营收益，按规定计入职业年金个人账户。"
    ],
    ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7"]
)

results = collection.query(
    query_texts=["职业年金缴用占比"], # Chroma will embed this for you
    n_results=3 # how many results to return
)

print(results)










from langchain_docling.loader import DoclingLoader

FILE_PATH = r"F:\train\docx\国办发2015_18号_机关事业单位职业年金办法.docx"

loader = DoclingLoader(file_path=FILE_PATH)

# Load all documents
documents = loader.load()

resuls=[]

for document in documents:
    print(document.page_content)
    document.page_content.split("AAAAAAAAAA")
    print('---------------------')