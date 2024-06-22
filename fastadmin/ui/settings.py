from pathlib import Path

import fastadmin.constants as const
import os


BASE_DIR = Path(__file__).parent.parent.parent
ENV = os.environ

PAGE_TITLE = ENV.get(const.DEFAULT_TITLE_PAGE)
API_ROOT_URL = ENV.get(const.API_ROOT_URL)
API_PATH_MODE = ENV.get(const.API_PATH_MODE, None)
API_PATH_STRIP = ENV.get(const.API_PATH_STRIP, None)
