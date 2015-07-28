import pycman
import pycman.transaction
import logging


class VSNUpdater:
    def __init__(self, pkgs_to_update: list):
        self.__options = pycman.action_sync.parse_options(None)
        self.__handle = pycman.action_sync.config.init_with_config_and_options(self.__options)
        self.__pkgs = pkgs_to_update

    def __refresh(self):
        force = (self.__options.refresh > 1)
        for db in self.__handle.get_syncdbs():
            t = pycman.transaction.init_from_options(self.__handle, self.__options)
            db.update(force)
            t.release()

    def __update(self):
        repos = dict((db.name, db) for db in self.__handle.get_syncdbs())
        if len(self.__pkgs) == 0:
            return False

        targets = []
        for name in self.__pkgs:
            ok, pkg = pycman.action_sync.find_sync_package(name, repos)
            if not ok:
                logging.error(pkg)
                return False
            else:
                targets.append(pkg)
        t = pycman.transaction.init_from_options(self.__handle, self.__options)
        [t.add_pkg(pkg) for pkg in targets]
        return pycman.transaction.finalize(t)

    def update(self):
        """Refresh database and update"""
        try:
            self.__refresh()
            self.__update()
        except Exception as message:
            logging.error(message)
