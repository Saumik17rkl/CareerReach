import pandas as pd

def normalize_columns(columns):
    return {col.lower().strip(): col for col in columns}


def parse_excel(file):
    import pandas as pd

    xls = pd.ExcelFile(file, engine="openpyxl")
    sheet_data = {}

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        col_map = normalize_columns(df.columns)

        records = []

        for _, row in df.iterrows():

            def get(col_names):
                for name in col_names:
                    key = name.lower()
                    if key in col_map:
                        return row[col_map[key]]
                return None

            record = {
                "company_name": get(["company name", "company"]),
                "hr_name": get(["hr name", "name"]),
                "email": get(["email", "mail"]),
                "mobile": get(["mobile", "phone number", "phone"]),
    "landline": get(["landline"]),
                "role": get(["role/department", "designation"]),
                "location": get(["location"]),
                "source_sheet": sheet
            }

            records.append(record)

        sheet_data[sheet] = records

    return sheet_data