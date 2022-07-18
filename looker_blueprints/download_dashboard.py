import argparse
import sys
import time
import os
import shipyard_utils as shipyard
from looker_sdk import models
from looker_sdk import sdk_exceptions
try:
    import helpers
except BaseException:
    from . import helpers


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument('--dashboard-id', dest='dashboard_id', required=True)
    parser.add_argument('--output-width', dest='output_width', required=True)
    parser.add_argument('--output-height', dest='output_height', required=True)
    parser.add_argument('--dest-file-name', dest='dest_file_name', required=True)
    parser.add_argument('--dest-folder-name', dest='dest_folder_name', required=False)
    parser.add_argument('--file-type', dest='file_type',
                        choices=['pdf', 'png', 'jpg'],
                        type=str.lower,
                        required=True)
    args = parser.parse_args()
    return args


def download_dashboard(sdk, dashboard_id, width, height, file_format):
    """Download specified dashboard using ID
    
    Returns:
        result: raw binary data of the dashboard
    """
    id = int(dashboard_id)
    task = sdk.create_dashboard_render_task(
        id,
        file_format,
        models.CreateDashboardRenderTask(
            dashboard_style='tiled',
            dashboard_filters=None,
        ),
        width,
        height,
    )

    if not (task and task.id):
        raise sdk_exceptions.RenderTaskError(
            f'Could not create a render task for "{dashboard_id}"'
        )

    # poll the render task until it completes
    elapsed = 0.0
    delay = 0.5  # wait .5 seconds
    while True:
        poll = sdk.render_task(task.id)
        if poll.status == "failure":
            print(poll)
            raise sdk_exceptions.RenderTaskError(
                f'Render failed for "{dashboard_id}"'
            )
        elif poll.status == "success":
            break

        time.sleep(delay)
        elapsed += delay
    print(f"Render task completed in {elapsed} seconds")

    result = sdk.render_task_results(task.id)
    return result



def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    file_type = args.file_type
    dashboard_id = args.dashboard_id
    dest_file_name = args.dest_file_name
    dest_folder_name = args.dest_folder_name
    
    # get cwd if no folder name is specified
    if not dest_folder_name:
        dest_folder_name = os.getcwd()
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name,
        dest_file_name
    )
    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    
    # download look and write to file
    width = args.output_width
    height = args.output_height
    result = download_dashboard(look_sdk, dashboard_id, width, height, file_type)

    with open(destination_file_path, 'wb+') as f:
        f.write(result)


if __name__ == "__main__":
    main()
    