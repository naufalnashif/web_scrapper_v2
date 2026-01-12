import pandas as pd
import json
import io

def get_download_link(data_list, format_type):
    df = pd.DataFrame(data_list)
    output = io.BytesIO()
    
    if format_type == "CSV":
        return df.to_csv(index=False).encode('utf-8'), "text/csv"
    
    elif format_type == "Excel":
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    elif format_type == "JSON":
        return json.dumps(data_list, indent=4).encode('utf-8'), "application/json"
    
    elif format_type == "TXT":
        return df.to_string(index=False).encode('utf-8'), "text/plain"
    
    
    return None, None