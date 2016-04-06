from os.path import basename

from . import (auth, dashboard, diskspace, emergency_reset, filemanager, lang,
               logs, notifications, ondd, settings, setup)


def routes(config):
    skip_plugins = config['app.skip_plugins']
    return (
        ('auth:login_form', auth.show_login_form,
         'GET', '/login/', {}),
        ('auth:login', auth.login,
         'POST', '/login/', {}),
        ('auth:logout', auth.logout,
         'GET', '/logout/', {}),
        ('auth:reset_form', auth.show_reset_form,
         'GET', '/reset-password/', {}),
        ('auth:reset', auth.reset,
         'POST', '/reset-password/', {}),
        ('emergency:reset_form', emergency_reset.show_emergency_reset_form,
         'GET', '/emergency/', {'skip': ['sessions']}),
        ('emergency:reset', emergency_reset.reset,
         'POST', '/emergency/', {'skip': ['sessions']}),
        ('dashboard:main', dashboard.dashboard,
         'GET', '/dashboard/', {}),
        ('diskspace:show_consolidate_form', diskspace.show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', diskspace.schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate_state', diskspace.consolidate_state,
         'GET', '/diskspace/consolidate/state', {})
        ('files:list', filemanager.init_file_action,
         'GET', '/files/', dict(unlocked=True)),
        ('files:path', filemanager.init_file_action,
         'GET', '/files/<path:path>', dict(unlocked=True)),
        ('files:action', filemanager.handle_file_action,
         'POST', '/files/<path:path>', dict(unlocked=True)),
        ('files:direct', filemanager.direct_file,
         'GET', '/direct/<path:path>', dict(unlocked=True)),
        ('ui:lang_list', lang.lang_list,
         'GET', '/languages/', {}),
        ('sys:applog', logs.send_applog,
         'GET', '/' + basename(config['logging.output']), dict(unlocked=True)),
        ('sys:syslog', logs.send_diags,
         'GET', '/syslog', dict(unlocked=True)),
        ('notifications:list', notifications.notification_list,
         'GET', '/notifications/', {}),
        ('notifications:read', notifications.notifications_read,
         'POST', '/notifications/', {}),
        ('ondd:status', ondd.get_signal_status,
         'GET', '/ondd/status/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:files', ondd.show_file_list,
         'GET', '/ondd/files/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:cache_status', ondd.show_cache_status,
         'GET', '/ondd/cache/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:settings', ondd.show_settings_form,
         'GET', '/ondd/settings/', dict(unlocked=True)),
        ('ondd:settings', ondd.set_settings,
         'POST', '/ondd/settings/', dict(unlocked=True)),
        ('settings:load', settings.show_settings_form,
         'GET', '/settings/', dict(unlocked=True)),
        ('settings:save', settings.save_settings,
         'POST', '/settings/', dict(unlocked=True)),
        ('setup:main', setup.enter_wizard,
         ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', setup.exit_wizard,
         'GET', '/setup/exit/', {}),
        ('setup:diag', setup.diag,
         'GET', '/diag/', {}),
    )
