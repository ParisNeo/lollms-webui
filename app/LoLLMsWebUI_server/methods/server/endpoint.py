def add_all_endpoints(self):
    self.add_endpoint(
        "/get_current_personality_files_list", "get_current_personality_files_list", self.get_current_personality_files_list, methods=["GET"]
    )
    self.add_endpoint(
        "/clear_personality_files_list", "clear_personality_files_list", self.clear_personality_files_list, methods=["GET"]
    )

    self.add_endpoint("/start_training", "start_training", self.start_training, methods=["POST"])

    self.add_endpoint("/get_lollms_version", "get_lollms_version", self.get_lollms_version, methods=["GET"])
    self.add_endpoint("/get_lollms_webui_version", "get_lollms_webui_version", self.get_lollms_webui_version, methods=["GET"])


    self.add_endpoint("/reload_binding", "reload_binding", self.reload_binding, methods=["POST"])
    self.add_endpoint("/update_software", "update_software", self.update_software, methods=["GET"])
    self.add_endpoint("/clear_uploads", "clear_uploads", self.clear_uploads, methods=["GET"])
    self.add_endpoint("/selectdb", "selectdb", self.selectdb, methods=["GET"])

    self.add_endpoint("/restart_program", "restart_program", self.restart_program, methods=["GET"])

    self.add_endpoint("/check_update", "check_update", self.check_update, methods=["GET"])



    self.add_endpoint("/post_to_personality", "post_to_personality", self.post_to_personality, methods=["POST"])


    self.add_endpoint("/install_model_from_path", "install_model_from_path", self.install_model_from_path, methods=["GET"])

    self.add_endpoint("/unInstall_binding", "unInstall_binding", self.unInstall_binding, methods=["POST"])
    self.add_endpoint("/reinstall_binding", "reinstall_binding", self.reinstall_binding, methods=["POST"])
    self.add_endpoint("/reinstall_personality", "reinstall_personality", self.reinstall_personality, methods=["POST"])

    self.add_endpoint("/switch_personal_path", "switch_personal_path", self.switch_personal_path, methods=["POST"])

    self.add_endpoint("/add_reference_to_local_model", "add_reference_to_local_model", self.add_reference_to_local_model, methods=["POST"])


    self.add_endpoint("/add_model_reference", "add_model_reference", self.add_model_reference, methods=["POST"])

    self.add_endpoint("/upload_model", "upload_model", self.upload_model, methods=["POST"])
    self.add_endpoint("/upload_avatar", "upload_avatar", self.upload_avatar, methods=["POST"])


    self.add_endpoint("/list_mounted_personalities", "list_mounted_personalities", self.list_mounted_personalities, methods=["POST"])

    self.add_endpoint("/mount_personality", "mount_personality", self.p_mount_personality, methods=["POST"])
    self.add_endpoint("/remount_personality", "remount_personality", self.p_remount_personality, methods=["POST"])

    self.add_endpoint("/unmount_personality", "unmount_personality", self.p_unmount_personality, methods=["POST"])        
    self.add_endpoint("/select_personality", "select_personality", self.p_select_personality, methods=["POST"])

    self.add_endpoint("/get_personality_settings", "get_personality_settings", self.get_personality_settings, methods=["POST"])

    self.add_endpoint("/get_active_personality_settings", "get_active_personality_settings", self.get_active_personality_settings, methods=["GET"])
    self.add_endpoint("/get_active_binding_settings", "get_active_binding_settings", self.get_active_binding_settings, methods=["GET"])

    self.add_endpoint("/set_active_personality_settings", "set_active_personality_settings", self.set_active_personality_settings, methods=["POST"])
    self.add_endpoint("/set_active_binding_settings", "set_active_binding_settings", self.set_active_binding_settings, methods=["POST"])

    self.add_endpoint(
        "/disk_usage", "disk_usage", self.disk_usage, methods=["GET"]
    )

    self.add_endpoint(
        "/ram_usage", "ram_usage", self.ram_usage, methods=["GET"]
    )
    self.add_endpoint(
        "/vram_usage", "vram_usage", self.vram_usage, methods=["GET"]
    )


    self.add_endpoint(
        "/list_bindings", "list_bindings", self.list_bindings, methods=["GET"]
    )
    self.add_endpoint(
        "/list_extensions", "list_extensions", self.list_extensions, methods=["GET"]
    )

    self.add_endpoint(
        "/list_models", "list_models", self.list_models, methods=["GET"]
    )
    self.add_endpoint(
        "/get_active_model", "get_active_model", self.get_active_model, methods=["GET"]
    )

    self.add_endpoint(
        "/list_personalities_categories", "list_personalities_categories", self.list_personalities_categories, methods=["GET"]
    )
    self.add_endpoint(
        "/list_personalities", "list_personalities", self.list_personalities, methods=["GET"]
    )

    self.add_endpoint(
        "/list_discussions", "list_discussions", self.list_discussions, methods=["GET"]
    )

    self.add_endpoint("/delete_personality", "delete_personality", self.delete_personality, methods=["GET"])
            
    self.add_endpoint("/", "", self.index, methods=["GET"])
    self.add_endpoint("/settings/", "", self.index, methods=["GET"])
    self.add_endpoint("/playground/", "", self.index, methods=["GET"])

    self.add_endpoint("/<path:filename>", "serve_static", self.serve_static, methods=["GET"])
    self.add_endpoint("/user_infos/<path:filename>", "serve_user_infos", self.serve_user_infos, methods=["GET"])

    self.add_endpoint("/images/<path:filename>", "serve_images", self.serve_images, methods=["GET"])
    self.add_endpoint("/bindings/<path:filename>", "serve_bindings", self.serve_bindings, methods=["GET"])
    self.add_endpoint("/personalities/<path:filename>", "serve_personalities", self.serve_personalities, methods=["GET"])
    self.add_endpoint("/outputs/<path:filename>", "serve_outputs", self.serve_outputs, methods=["GET"])
    self.add_endpoint("/data/<path:filename>", "serve_data", self.serve_data, methods=["GET"])
    self.add_endpoint("/help/<path:filename>", "serve_help", self.serve_help, methods=["GET"])

    self.add_endpoint("/uploads/<path:filename>", "serve_uploads", self.serve_uploads, methods=["GET"])


    self.add_endpoint("/export_discussion", "export_discussion", self.export_discussion, methods=["GET"])
    self.add_endpoint("/export", "export", self.export, methods=["GET"])

    self.add_endpoint("/stop_gen", "stop_gen", self.stop_gen, methods=["GET"])

    self.add_endpoint("/rename", "rename", self.rename, methods=["POST"])
    self.add_endpoint("/edit_title", "edit_title", self.edit_title, methods=["POST"])

    self.add_endpoint(
        "/delete_discussion",
        "delete_discussion",
        self.delete_discussion,
        methods=["POST"],
    )

    self.add_endpoint(
        "/edit_message", "edit_message", self.edit_message, methods=["GET"]
    )
    self.add_endpoint(
        "/message_rank_up", "message_rank_up", self.message_rank_up, methods=["GET"]
    )
    self.add_endpoint(
        "/message_rank_down", "message_rank_down", self.message_rank_down, methods=["GET"]
    )
    self.add_endpoint(
        "/delete_message", "delete_message", self.delete_message, methods=["GET"]
    )


    self.add_endpoint(
        "/get_config", "get_config", self.get_config, methods=["GET"]
    )

    self.add_endpoint(
        "/get_current_personality_path_infos", "get_current_personality_path_infos", self.get_current_personality_path_infos, methods=["GET"]
    )

    self.add_endpoint(
        "/get_available_models", "get_available_models", self.get_available_models, methods=["GET"]
    )


    self.add_endpoint(
        "/extensions", "extensions", self.extensions, methods=["GET"]
    )

    self.add_endpoint(
        "/upgrade_to_gpu", "upgrade_to_gpu", self.upgrade_to_gpu, methods=["GET"]
    )

    self.add_endpoint(
        "/training", "training", self.training, methods=["GET"]
    )
    self.add_endpoint(
        "/main", "main", self.main, methods=["GET"]
    )

    self.add_endpoint(
        "/settings", "settings", self.settings, methods=["GET"]
    )

    self.add_endpoint(
        "/help", "help", self.help, methods=["GET"]
    )

    self.add_endpoint(
        "/get_generation_status", "get_generation_status", self.get_generation_status, methods=["GET"]
    )

    self.add_endpoint(
        "/update_setting", "update_setting", self.update_setting, methods=["POST"]
    )
    self.add_endpoint(
        "/apply_settings", "apply_settings", self.apply_settings, methods=["POST"]
    )


    self.add_endpoint(
        "/save_settings", "save_settings", self.save_settings, methods=["POST"]
    )

    self.add_endpoint(
        "/get_current_personality", "get_current_personality", self.get_current_personality, methods=["GET"]
    )


    self.add_endpoint(
        "/get_all_personalities", "get_all_personalities", self.get_all_personalities, methods=["GET"]
    )

    self.add_endpoint(
        "/get_personality", "get_personality", self.get_personality, methods=["GET"]
    )


    self.add_endpoint(
        "/reset", "reset", self.reset, methods=["GET"]
    )

    self.add_endpoint(
        "/export_multiple_discussions", "export_multiple_discussions", self.export_multiple_discussions, methods=["POST"]
    )      
    self.add_endpoint(
        "/import_multiple_discussions", "import_multiple_discussions", self.import_multiple_discussions, methods=["POST"]
    )      

    self.add_endpoint(
        "/get_presets", "get_presets", self.get_presets, methods=["GET"]
    )      

    self.add_endpoint(
        "/add_preset", "add_preset", self.add_preset, methods=["POST"]
    )

    self.add_endpoint(
        "/save_presets", "save_presets", self.save_presets, methods=["POST"]
    )

    self.add_endpoint(
        "/execute_python_code", "execute_python_code", self.execute_python_code, methods=["POST"]
    )