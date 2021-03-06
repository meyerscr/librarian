<%inherit file="_playlist.tpl" />

<%def name="audio_control(url)">
    <div id="audio-controls-audio-wrapper" class="audio-controls-audio-wrapper">
        <audio id="audio-controls-audio" controls="controls">
            <source src="${url | h}" />
            <object type="application/x-shockwave-flash" data="${assets.url}vendor/mediaelement/flashmediaelement.swf">
                <param name="movie" value="${assets.url}vendor/mediaelement/flashmediaelement.swf" />
                <param name="flashvars" value="controls=true&file=${url | h}" />
            </object>
        </audio>
    </div>
</%def>

<%def name="view_main()">
    % if 'audio' not in current.meta.content_type_names:
        <span class="note">${_('No music files to be played.')}</span>
    % else:
        <%
        selected_entry = selected
        thumb_path = th.facets.get_thumb_path(selected_entry.rel_path, default=None)
        if thumb_path:
            cover_url = h.quoted_url('filemanager:direct', path=thumb_path)
            custom_cover = True
        else:
            cover_url = assets.url + 'img/albumart-placeholder.png'
            custom_cover = False

        audio_url = h.quoted_url('filemanager:direct', path=selected_entry.rel_path)
        metadata = selected_entry.meta
        %>
        <div class="audio-controls" id="audio-controls">
            <div class="audio-controls-albumart" id="audio-controls-albumart">
                <img src="${cover_url}" class="audio-controls-cover${' audio-controls-custom-cover' if custom_cover else ''}">
                <div class="audio-controls-title" id="audio-controls-title">
                    <h2>${metadata.get('title') or th.facets.titlify(selected_entry.name)}</h2>
                    <p>${metadata.get('author', default=_('Unknown author'))}</p>
                </div>
            </div>
            ${audio_control(audio_url)}
        </div>
        <script type="application/json" id="audioData">
          {
            "defaultThumbUrl": "${assets.url + 'img/albumart-placeholder.png'}"
          }
        </script>
    % endif
</%def>

<%def name="sidebar()">
    % if 'audio' in current.meta.content_type_names:
        ${self.sidebar_playlist(files, selected)}
    % endif
</%def>

<%def name="sidebar_playlist_item_metadata(entry)">
    <% metadata = entry.meta %>
    ${self.sidebar_playlist_item_metadata_desc(metadata)}
    ${self.sidebar_playlist_item_metadata_author(metadata)}
    ${self.sidebar_playlist_item_metadata_album(metadata)}
    ${self.sidebar_playlist_item_metadata_genre(metadata)}
    ${self.sidebar_playlist_item_metadata_duration(metadata)}
</%def>

<%def name="sidebar_playlist_item(entry, selected_entry)">
    <%
    file = entry.name
    current = entry.name == selected_entry.name
    file_path = entry.rel_path
    mimetype = entry.meta.mime_type or ''
    url = i18n_url('filemanager:list', view=view, path=path, selected=file)
    meta_url = i18n_url('filemanager:details', view=view, path=path, info=file)
    direct_url = h.quoted_url('filemanager:direct', path=file_path)
    get_thumb_url = i18n_url('filemanager:thumb', path=file_path, facet='audio')
    metadata = entry.meta
    title = metadata.get('title') or th.facets.titlify(file)
    author = metadata.get('author') or _('Unknown Artist')
    duration = metadata.get('duration', default=0)
    hduration = th.facets.durify(duration)
    size = metadata.get('size', default=0)
    %>
    <li
        class="playlist-list-item ${'playlist-list-item-current' if current else ''}"
        role="row"
        aria-selected="false"
        data-title="${title | h}"
        data-author="${author | h}"
        data-duration="${duration}"
        data-mimetype="${mimetype | h}"
        data-type="file"
        data-relpath="${file_path | h.urlquote}"
        data-url="${url}"
        data-meta-url="${meta_url}"
        data-direct-url="${direct_url}"
        data-get-thumb-url="${get_thumb_url}"
        data-file-size="${size}">
        <a class="playlist-list-item-link" href="${url}">
            <span class="playlist-list-duration">${hduration}</span>
            <span class="playlist-list-title">${title | h} - ${author | h}</span>
        </a>
    </li>
</%def>

${self.view_main()}
