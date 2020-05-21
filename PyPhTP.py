import argparse
import os
import shutil
import sqlite3
import subprocess
import sys


class PhTP:

    def __init__(self):

        self.path_pihole_dir = r'/etc/pihole'
        self.path_pihole_db = os.path.join(self.path_pihole_dir, 'gravity.db')
        self.path_output_dir = os.path.join(self.path_pihole_dir, 'PhTP')
        self.path_output_db = os.path.join(self.path_output_dir, 'gravity.db')
        self.connection = None
        self.cursor = None

    def access_check(self):

        if os.path.exists(self.path_pihole_dir):
            print('[i] Pi-hole directory located')
            if os.access(self.path_pihole_dir, os.X_OK | os.W_OK):
                print('[i] Write access is available to Pi-hole directory')
                # Does the DB exist
                # and is the file size greater than 0 bytes
                if os.path.isfile(self.path_pihole_db) and os.path.getsize(self.path_pihole_db) > 0:
                    print('[i] Pi-hole DB located')
                    return True
                else:
                    print('[e] Write access is available but the Pi-hole DB does not exist')
                    return False
            else:
                print('[e] Write access is not available to the Pi-hole directory.')
                return False
        else:
            print('[e] Pi-hole directory was not found!')
            return False

    def make_connection(self):

        try:
            self.connection = sqlite3.connect(self.path_pihole_db)
        except sqlite3.Error as e:
            print('[e] Failed to connected to Pi-hole DB')
            return False

        print('[i] Connection established to Pi-hole DB')

        self.cursor = self.connection.cursor()

        return True

    def shrink_db(self):

        # Display size of DB
        print(f'[i] gravity.db size: {round(os.path.getsize(self.path_pihole_db)/(1024*1024), 2)} MB')

        # Remove gravity table entries
        print('[i] Emptying the gravity table')
        self.cursor.execute('DELETE FROM gravity;')
        self.connection.commit()

        # Run Vacuum
        print('[i] Running Vacuum')
        self.connection.execute('VACUUM')

        # Display size of DB
        print(f'[i] gravity.db size: {round(os.path.getsize(self.path_pihole_db) / (1024 * 1024), 2)} MB')

    def move_db(self, option='eject'):

        # Determine valid options
        valid_options = {'eject', 'inject'}

        # If a valid option was passed
        if option in valid_options:
            if option == 'eject':
                # Use shutil to copy
                print(f'[i] Copying gravity.db to {self.path_output_db}')
                shutil.copy2(self.path_pihole_db, self.path_output_db)

                # Correct owner etc.
                print('[i] Correcting permissions')
                st = os.stat(self.path_pihole_db)
                os.chown(self.path_output_db, st.st_uid, st.st_gid)

                # Update gravity
                refresh_gravity()

            elif option == 'inject':
                # Check that a gravity file exists
                print(f'[i] Checking whether {self.path_output_db} exists')
                if os.path.isfile(self.path_output_db) and os.path.getsize(self.path_output_db) > 0:
                    # Grab owner etc
                    st = os.stat(self.path_output_db)
                    # Overwrite the Pi-hole DB
                    print('[i] Overwriting Pi-hole DB')
                    shutil.move(self.path_output_db, self.path_pihole_db)
                    # Correct owner etc.
                    print('[i] Correcting permissions')
                    os.chown(self.path_pihole_db, st.st_uid, st.st_gid)

                    # Update gravity
                    refresh_gravity()
                else:
                    print('[i] There is no DB to pull')
                    return False
        else:
            return False

    def close_connection(self):

        print('[i] Closing connection to the Pi-hole DB')
        self.connection.close()

    def stage_output(self):
        # Create /etc/pihole/PyPhDB
        if not os.path.exists(self.path_output_dir):
            print('[i] Creating output directory')
            os.mkdir(self.path_output_dir)

    def clean_dump(self):
        if os.path.isfile(self.path_output_db):
            print(f'[i] Removing DB dump')
            os.remove(self.path_output_db)
        else:
            print('[i] There is no DB dump to clean')


def refresh_gravity():

    print('[i] Refreshing Gravity for source database')
    subprocess.call(['pihole', '-g'], stdout=subprocess.DEVNULL)


# Create a new argument parser
parser = argparse.ArgumentParser()
# Create mutual exclusion groups
group_action = parser.add_mutually_exclusive_group()
# Dump flag
group_action.add_argument('-e', '--eject', help='Eject pi-hole DB to output directory', action='store_true')
# Upload flag
group_action.add_argument('-i', '--inject', help='Pull pi-hole DB from output directory', action='store_true')
# Clean flag
group_action.add_argument('-c', '--clean', help='Clean (remove) the output directory', action='store_true')
# Parse arguments
args = parser.parse_args()

# If no arguments were passed
if not len(sys.argv) > 1:
    print('[i] No script arguments detected - Defaulted to Push')
    # Default to dump mode
    args.eject = True

# Create a new teleporter instance
PhTP_inst = PhTP()

# If there is access to the Pi-hole dir
if PhTP_inst.access_check():
    # Stage output area for inject / eject
    PhTP_inst.stage_output()
    # If the clean flag is enabled
    if args.clean:
        PhTP_inst.clean_dump()
        exit()
    # If the push flag is set
    if args.eject:
        # If we make a connection to the DB
        if PhTP_inst.make_connection():
            # Shrink the DB by removing the entries from gravity
            PhTP_inst.shrink_db()
            # Close the connection to the DB
            PhTP_inst.close_connection()
            # Moe the database
            PhTP_inst.move_db('eject')
    # If the inject flag is set
    elif args.inject:
        # Overwrite Pi-hole DB
        PhTP_inst.move_db('inject')
