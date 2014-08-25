"""
content.py: routes related to content

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat
import math
import logging

from bottle import request, view, abort, default_app

from ..lib import archive
from ..lib import downloads
from ..lib import send_file

__all__ = ('app', 'content_list', 'content_file', 'content_index',)

PREFIX = '/content'
CONTENT_ID = '<content_id:re:[0-9a-f]{32}>'


app = default_app()


@app.get(PREFIX + '/')
@view('content_list')
def content_list():
    """ Show list of content """
    try:
        f_per_page = int(request.params.get('c', 1))
    except ValueError as e:
        f_per_page = 1
    f_per_page = max(1, min(4, f_per_page))
    try:
        page = int(request.params.get('p', 1))
    except ValueError:
        page = 1
    query = request.params.getunicode('q', '').strip()

    per_page = f_per_page * 20

    if query:
        total_items = archive.get_search_count(query)
    else:
        total_items = archive.get_count()

    total_pages = math.ceil(total_items / per_page)
    page = max(1, min(total_pages, page))
    offset = (page - 1) * per_page

    if query:
        metadata = archive.search_content(query, offset, per_page)
    else:
        metadata = archive.get_content(offset, per_page)

    return {
        'metadata': metadata,
        'total_items': total_items,
        'total_pages': total_pages,
        'per_page': per_page,
        'f_per_page': f_per_page,
        'page': page,
        'vals': request.params.decode(),
        'query': query,
    }


@app.get(PREFIX + '/%s/<filename>' % CONTENT_ID)
def content_file(content_id, filename):
    """ Serve file from zipball with specified id """
    zippath = downloads.get_zip_path(content_id)
    try:
        metadata, content = downloads.get_file(zippath, filename)
    except KeyError:
        logging.debug("File '%s' not found in '%s'" % (filename, zippath))
        abort(404, 'Not found')
    size = metadata.file_size
    timestamp = os.stat(zippath)[stat.ST_MTIME]
    if filename.endswith('.html'):
        logging.debug("Patching HTML file '%s' with Librarian stylesheet" % (
                      filename))
        # Patch HTML with link to stylesheet
        size, content = downloads.patch_html(content)
    return send_file.send_file(content, filename, size, timestamp)


@app.get(PREFIX + '/%s/' % CONTENT_ID)
def content_index(content_id):
    """ Shorthand for /<content_id>/index.html """
    archive.add_view(content_id)
    return content_file(content_id, 'index.html')

