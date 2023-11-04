import os
from datetime import datetime, timedelta
dirs = ['all_chests', 'chest_names', 'chest_types',
        'full_chests', 'ttl', 'player_names']
now = datetime.now()
two_weeks = now-timedelta(days=12)


def clear_dir(direction):
    folder_path = os.path.join('temp_images', direction)
    files = os.listdir(folder_path)
    for filename in files:
        filename_path = os.path.join('temp_images', direction, filename)
        mod_timestamp = os.path.getmtime(filename_path)
        mod_datetime = datetime.fromtimestamp(mod_timestamp)
        if(mod_datetime < two_weeks):
            os.remove(filename_path)


for cur_dir in dirs:
    clear_dir(cur_dir)
