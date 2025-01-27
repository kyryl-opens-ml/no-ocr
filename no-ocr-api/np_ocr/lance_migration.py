import lancedb
import numpy as np
import pyarrow as pa

db = lancedb.connect("lance-db-data/qwe123")
schema = pa.schema(
    [
        pa.field("id", pa.int64()),
        # float16, float32, and float64 are supported
        pa.field("vector", pa.list_(pa.list_(pa.float32(), 128))),
    ]
)
data = [
    {
        "id": i,
        "vector": np.random.random(size=(1030, 128)).tolist(),
    }
    for i in range(1024)
]
tbl = db.create_table("my_table", data=data, schema=schema)

# only cosine similarity is supported for multi-vectors
tbl.create_index(metric="cosine")

# query with multiple vectors
query = np.random.random(size=(13, 128))
print(tbl.search(query).to_arrow())
