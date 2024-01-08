import requests
import json

URL = 'https://ra.co/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Referer': 'https://ra.co/events/de/berlin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

def fetch_graphql_schema():
    introspection_query = {
        "query": """
            query IntrospectionQuery {
              __schema {
                types {
                  name
                  kind
                  description
                  fields {
                    name
                    description
                  }
                }
              }
            }
        """
    }

    response = requests.post(URL, headers=HEADERS, json=introspection_query)

    try:
        response.raise_for_status()
        schema_data = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error: {str(e)}")
        return None

    if 'data' not in schema_data:
        print(f"Error: {schema_data}")
        return None

    return schema_data['data']['__schema']['types']

def print_schema(types):
    for t in types:
        print(f"Type: {t['name']} - Kind: {t['kind']}")
        print(f"Description: {t['description']}")
        
        if 'fields' in t and t['fields'] is not None:
            print("Fields:")
            for field in t['fields']:
                print(f"  - {field['name']} - {field['description']}")
        else:
            print("No fields information available.")
            
        print("-" * 80)

def save_schema_to_file(types, filename='graphql_schema.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for t in types:
            file.write(f"Type: {t['name']} - Kind: {t['kind']}\n")
            file.write(f"Description: {t['description']}\n")
            
            if 'fields' in t and t['fields'] is not None:
                file.write("Fields:\n")
                for field in t['fields']:
                    file.write(f"  - {field['name']} - {field['description']}\n")
            else:
                file.write("No fields information available.\n")
                
            file.write("-" * 80 + '\n')

def main():
    schema_types = fetch_graphql_schema()

    if schema_types:
        save_schema_to_file(schema_types)
        print("Schema information saved to 'graphql_schema.txt'.")

if __name__ == "__main__":
    main()
