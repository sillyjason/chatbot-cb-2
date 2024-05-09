from datetime import datetime
import re

    
def data_reformat(data):    
    # Process "last_update" field
    last_update = data.get('last_update', None)
    if last_update is not None:
        if isinstance(last_update, int):  # Unix timestamp in seconds
            data['last_update'] = datetime.fromtimestamp(last_update).strftime('%Y/%m/%d %H:%M:%S')
        elif isinstance(last_update, str):
            if last_update.isdigit():  # Unix timestamp in seconds but as a string
                data['last_update'] = datetime.fromtimestamp(int(last_update)).strftime('%Y/%m/%d %H:%M:%S')
            else:  # Date time string
                try:
                    data['last_update'] = datetime.strptime(last_update, '%Y/%m/%d %H:%M:%S').strftime('%Y/%m/%d %H:%M:%S')
                except ValueError:
                    print(f"Invalid date format for 'last_update': {last_update}")

    # Process "product_promotion_details", "product_details", "product_exclusions" fields
    for field in ['product_promotion_details', 'product_details', 'product_exclusions']:
        value = data.get(field, None)
        if value is not None and isinstance(value, str):
            # Remove line breaks and extra spaces
            data[field] = re.sub(r'\s+', ' ', value.replace('\n', '').strip())

    return data