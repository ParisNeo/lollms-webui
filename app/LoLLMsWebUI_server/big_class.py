from lollms.paths import LollmsPaths
from lollms.binding import LOLLMSConfig
from lollms.main_config import LOLLMSConfig
from api import LoLLMsAPPI


class LoLLMsWebUI(LoLLMsAPPI):
    def __init__(self, args, _app, _socketio, config:LOLLMSConfig, config_file_path:Path|str, lollms_paths:LollmsPaths) -> None:
        self.args = args
        if len(config.personalities)==0:
            config.personalities.append("generic/lollms")
            config["active_personality_id"] = 0
            config.save_config()

        if config["active_personality_id"]>=len(config["personalities"]) or config["active_personality_id"]<0:
            config["active_personality_id"] = 0
        super().__init__(config, _socketio, config_file_path, lollms_paths)

        if config.auto_update:
            if check_update_():
                ASCIIColors.info("New version found. Updating!")
                self.update_software()

        self.app = _app
        self.cancel_gen = False

        app.template_folder = "web/dist"

        if len(config["personalities"])>0:
            self.personality_category= config["personalities"][config["active_personality_id"]].split("/")[0]
            self.personality_name= config["personalities"][config["active_personality_id"]].split("/")[1]
        else:
            self.personality_category = "generic"
            self.personality_name = "lollms"

        self.add_all_endpoints()

    def add_endpoint(
        self,
        endpoint=None,
        endpoint_name=None,
        handler=None,
        methods=["GET"],
        *args,
        **kwargs,
    ):
        self.app.add_url_rule(
            endpoint, endpoint_name, handler, methods=methods, *args, **kwargs
        )

    from LoLLMsWebUI_server.methods.interaction.discussion import (
        export_multiple_discussions,
        import_multiple_discussions,
        rename,
        edit_title,
        delete_discussion,
        edit_message,
        message_rank_up,
        message_rank_down,
        delete_message,
    )
    from LoLLMsWebUI_server.methods.interaction.personality import (
        get_current_personality,
        get_all_personalities,
        get_personality,
        get_current_personality_files_list,
        clear_personality_files_list,
        p_mount_personality,
        p_remount_personality,
        p_unmount_personality,
        get_active_personality_settings,
        set_active_personality_settings,
        get_personality_settings,
        p_select_personality,
        get_current_personality_path_infos,
        delete_personality,
        reinstall_personality,
        post_to_personality,
    )
    from LoLLMsWebUI_server.methods.io.misc import (
        export,
        export_discussion,
        clear_uploads,
        selectdb,
    )
    from LoLLMsWebUI_server.methods.ML.generation import (
        get_generation_status,
        stop_gen,
    )
    from LoLLMsWebUI_server.methods.ML.models import (
        get_active_model,
        add_reference_to_local_model,
        install_model_from_path,
        add_model_reference,
        upload_model,
        get_available_models,
    )
    from LoLLMsWebUI_server.methods.ML.train import (
        start_training,
        train,
    )
    from LoLLMsWebUI_server.methods.process.lists import (
        list_bindings,
        list_extensions,
        list_models,
        list_personalities_categories,
        list_personalities,
        list_discussions,
        list_mounted_personalities,
    )
    from LoLLMsWebUI_server.methods.process.lollm_os import (
        execute_python_code,
        copy_files,
        reset,
        find_extension,
        restart_program,
    )
    from LoLLMsWebUI_server.methods.server.endpoint import (
        add_all_endpoints
    )
    from LoLLMsWebUI_server.methods.server.render import (
        main,
        settings,
        help,
        training,
        extensions,
        index,
    )
    from LoLLMsWebUI_server.methods.server.serve import (
        serve_static,
        serve_images,
        serve_bindings,
        serve_user_infos,
        serve_personalities,
        serve_outputs,
        serve_help,
        serve_data,
        serve_uploads,
    )
    from LoLLMsWebUI_server.methods.settings.bindings import (
        reinstall_binding,
        unInstall_binding,
        reload_binding,
        get_active_binding_settings,
        set_active_binding_settings,
    )
    from LoLLMsWebUI_server.methods.settings.hardware import (
        upgrade_to_gpu,
        ram_usage,
        vram_usage,
        disk_usage,
    )
    from LoLLMsWebUI_server.methods.settings.presets import (
        get_presets,
        add_preset,
        del_preset,
        save_presets
    )
    from LoLLMsWebUI_server.methods.settings.settings import (
        save_settings,
        update_setting,
        apply_settings,
        get_lollms_version,
        get_lollms_webui_version,
        get_config,
        switch_personal_path,
        upload_avatar,
    )
    from LoLLMsWebUI_server.methods.settings.updates import (
        update_software,
        check_update,
    )
    