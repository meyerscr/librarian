from os.path import basename

from bottle import error

from ..core.exts import ext_container as exts
from ..utils.filters import safepath_filter
from . import (auth, dashboard, diskspace, filemanager, lang, logs,
               notifications, ondd, settings, setup, system)


def routes(config):
    exts.bottle_app.router.add_filter('safepath', safepath_filter)
    error(403)(system.error_403)
    error(404)(system.error_404)
    error(500)(system.error_500)
    error(503)(system.error_503)
    auth.Login.route('/login/', app=exts.bottle_app)
    auth.Logout.route('/logout/', app=exts.bottle_app)
    auth.PasswordReset.route('/reset-password/', app=exts.bottle_app)
    auth.EmergencyReset.route('/emergency/', app=exts.bottle_app)
    filemanager.List.route('/files/<path:safepath>', app=exts.bottle_app)
    filemanager.Details.route('/details/<path:safepath>', app=exts.bottle_app)
    filemanager.Direct.route('/direct/<path:safepath>', app=exts.bottle_app)
    filemanager.Delete.route('/delete/<path:safepath>', app=exts.bottle_app)
    filemanager.Thumb.route('/thumb/<path:safepath>', app=exts.bottle_app)
    lang.List.route(app=exts.bottle_app)
    notifications.List.route(app=exts.bottle_app)
    ondd.Status.route(app=exts.bottle_app)
    ondd.FileList.route(app=exts.bottle_app)
    ondd.CacheStatus.route(app=exts.bottle_app)
    ondd.Settings.route(app=exts.bottle_app)
    settings.Settings.route(app=exts.bottle_app)
    route_config = (
        ('dashboard:main', dashboard.dashboard,
         'GET', '/dashboard/', {}),
        ('diskspace:show_consolidate_form', diskspace.show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', diskspace.schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate_state', diskspace.consolidate_state,
         'GET', '/diskspace/consolidate/state', {}),
        ('sys:applog', logs.send_applog,
         'GET', '/' + basename(config['logging.output']), dict(unlocked=True)),
        ('sys:syslog', logs.send_diags,
         'GET', '/syslog', dict(unlocked=True)),
        ('setup:main', setup.enter_wizard,
         ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', setup.exit_wizard,
         'GET', '/setup/exit/', {}),
        ('setup:diag', setup.diag,
         'GET', '/diag/', {}),
        # This route handler is added because unhandled missing pages cause
        # bottle to _not_ install any plugins, and some are essential to
        # rendering of the 404 page (e.g., i18n, sessions, auth).
        ('sys:all404', system.all_404,
         ['GET', 'POST'], '/<path:path>', dict()),
    )
    if config.get('app.default_route'):
        route_config = (
            ('sys:root', system.root_handler, 'GET', '/', dict()),
        ) + route_config
    return route_config
