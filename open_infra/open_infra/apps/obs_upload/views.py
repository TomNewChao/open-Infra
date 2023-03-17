import json
import traceback

from django.views import View

from obs_upload.resources.obs_upload_mgr import ObsInteractGitBase, ObsInteractMgr, ObsInteractComment
from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.common import assemble_api_result
from open_infra.utils.utils_git import GitHubPrStatus
from logging import getLogger

logger = getLogger("django")


class ObsInteractView(View):

    def post(self, request):
        """the api for github obs-interact"""
        dict_data = json.loads(request.body)
        if not GitHubPrStatus.is_in_github_pr_status(dict_data.get("action")):
            logger.error("[GitHubPrView] receive param fault:{}".format(dict_data.get("action")))
            return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS)
        obs_interact_git_base = ObsInteractGitBase(dict_data)
        try:
            ObsInteractMgr.get_obs_interact(obs_interact_git_base)
        except Exception as e:
            logger.error("[GitHubPrView] e:{}, traceback:{}".format(e, traceback.format_exc()))
            obs_interact_git_base.comment_pr(comment=ObsInteractComment.error)
        return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS)
