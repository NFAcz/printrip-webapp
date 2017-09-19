#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import argparse
import subprocess
import os
import sys
import yaml
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import time
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery

os.chdir(sys.path[0])
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Config file to use', default='{0}/config.yml'.format(sys.path[0]))
parser.add_argument('-l', '--listen', help='Listen address', default='127.0.0.1')
parser.add_argument('-p', '--port', help=' Listen port', default=5000)
parser.add_argument('-d', '--debug', help='Flask debug', action='store_true')
args = parser.parse_args()

config_file = args.config
cfg = yaml.load(open(config_file, mode='r'))
options = cfg['options']
recording = options['recording']
messages = cfg['messages']
output_dir = options['output_dir']
tmp_filepath = '{0}/{1}'.format(output_dir, options['tmp_filename'])

app = Flask(__name__)

ffmpeg_pid = 0
print_id = '000000'
title_name = ''
credentials = ServiceAccountCredentials.from_json_keyfile_name(cfg['credentials']['credential_path'],
                                                               scopes=cfg['credentials']['scopes'])
http_auth = credentials.authorize(Http())


def write_to_sheet(values):
    body = {'values': [values]}
    service = discovery.build('sheets', 'v4', http=http_auth,
                              discoveryServiceUrl=cfg['credentials']['sheets_discovery'])
    result = service.spreadsheets().values().append(spreadsheetId=cfg['credentials']['sheet_id'],
                                                    valueInputOption='RAW',
                                                    range=cfg['credentials']['sheet_range'],
                                                    body=body).execute()
    return result


def run_command(sound_type='none'):
    outputs = []

    for output in recording['outputs']:
        output_line = []
        for parameter in recording['output_param_order'].split(','):
            output_line.append(output[parameter])
        outputs.append(' '.join(output_line))

    command = '{0} | {1} {2}'.format(recording['input_cmd'], recording['output_cmd'], ' '.join(outputs))
    print command.format(sound_type=sound_type, tmp_filepath=tmp_filepath)
    p = subprocess.Popen(command.format(sound_type=sound_type, tmp_filepath=tmp_filepath), shell=True)
    return p


@app.route('/')
def root():
    msg = request.args.get('msg')
    filename = request.args.get('filename')

    if msg is not None:
        if filename is not None:
            msg = messages[msg].format(filename=filename)
        else:
            msg = messages[msg]
    else:
        if ffmpeg_pid is not 0:
            msg = messages['rec_running']
        else:
            msg = messages['idle']
    return render_template('root.html',
                           msg=msg, ffmpeg_pid=ffmpeg_pid, timestamp=int(time.time()),
                           print_id=print_id, title_name=title_name)


@app.route('/start', methods=['POST'])
def start():
    global ffmpeg_pid
    sound_type = request.form.get('sound_type')

    try:
        assert ffmpeg_pid is 0
        p = run_command(sound_type=recording['sound-type'][sound_type])
        ffmpeg_pid = p.pid
        return redirect(url_for('root', msg='rec_start_ok'))
    except AssertionError:
        return redirect(url_for('root', msg='rec_start_err'))


@app.route('/stop')
def stop():
    global ffmpeg_pid, print_id, title_name
    timestamp = int(time.time())

    try:
        assert ffmpeg_pid is not 0
        assert title_name != ''

        subprocess.call(recording['kill_command'], shell=True)
        ffmpeg_pid = 0
        dst_filename = options['dst_filename'].format(print_id=print_id, title_name=title_name.encode('utf-8'),
                                                      timestamp=timestamp)
        os.rename(tmp_filepath, '{0}/{1}'.format(output_dir, dst_filename))
        write_to_sheet([print_id, title_name, timestamp, 'http://{0}/download/{1}'.format(options['domain'], dst_filename)])
        print_id = '000000'
        title_name = ''
        return redirect(url_for('root', msg='rec_stop_ok', filename=dst_filename))
    except AssertionError:
        return redirect(url_for('root', msg='rec_stop_err'))


@app.route('/setname', methods=['POST'])
def setname():
    global print_id, title_name

    print_id = request.form.get('print_id').upper()
    # Select the custom name if the custom radio is checked - we don't need javascript with this :)
    if print_id == 'CUSTOM':
        print_id = request.form.get('print_id_custom').upper()
    title_name = request.form.get('title_name').replace(' ', '_').upper()
    return redirect(url_for('root'))


@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(directory=output_dir, filename=filename)


@app.route('/preview')
def preview():
    if ffmpeg_pid is 0:
        subprocess.call(options['preview_command'], shell=True)
    return redirect(url_for('root', msg='preview'))


if __name__ == '__main__':
    app.run(threaded=True, debug=args.debug, host=args.listen, port=int(args.port))
