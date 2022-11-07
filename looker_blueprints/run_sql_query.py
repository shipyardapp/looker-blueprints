import argparse
import sys
import os
import shipyard_utils as shipyard
try:
    import helpers
except BaseException:
    from . import helpers


EXIT_CODE_QUERY_ERROR = 203


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument('--slug', dest='slug', required=False)
    parser.add_argument('--dest-file-name', dest='dest_file_name', required=True)
    parser.add_argument('--dest-folder-name', dest='dest_folder_name', required=False)
    parser.add_argument('--file-type', dest='file_type',
                        choices=['inline_json', 'json', 'json_detail', 'json_fe', 'csv', 'html', 'md', 'txt', 'xlsx', 'gsxml', 'json_label'],
                        type=str.lower,
                        required=True)
    args = parser.parse_args()
    return args


def run_sql_query_and_download(sdk, slug, file_format):
    try:
        response = sdk.run_sql_query(slug=slug, result_format=file_format)
        print(f"SQL Query {slug} created successfully")
    except Exception as e:
        print(f'Error running create query: {e}')
        sys.exit(EXIT_CODE_QUERY_ERROR)
    return response


def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    file_type = args.file_type
    dest_file_name = args.dest_file_name

    # get cwd if no folder name is specified
    if args.dest_folder_name:
        # create folder path if non-existent
        shipyard.files.create_folder_if_dne(args.dest_folder_name)
        dest_folder_name = args.dest_folder_name
    else:
        dest_folder_name = os.getcwd()
    
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name,
        dest_file_name
    )
    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    if args.slug != "":
        slug = args.slug
    else:
        artifact_subfolder_paths = helpers.artifact_subfolder_paths
        slug = shipyard.logs.read_pickle_file(artifact_subfolder_paths, 
                                                    'slug')
        
    # download look and write to file
    result = run_sql_query_and_download(look_sdk, slug, file_type)
    
    with open(destination_file_path, 'wb+') as f:
        # convert to bytes if str
        if type(result) == str:
            result = bytes(result, 'utf-8')
        f.write(result)
    print(f"query with file: {dest_file_name} created successfully!")


if __name__ == "__main__":
    main()