from app.services.semantic_detector import detect_semantic_type


def infer_schema(df, domain="General"):

    schema = []

    for column, dtype in df.schema.items():

        sample_values = (
            df[column]
            .drop_nulls()
            .head(20)
            .to_list()
        )

        semantic_info = detect_semantic_type(
            column,
            sample_values,
            domain=domain
        )

        schema.append({
            "column_name": column,
            "data_type": str(dtype),
            "semantic_type": semantic_info["semantic_type"],
            "confidence": semantic_info["confidence"]
        })

    return schema