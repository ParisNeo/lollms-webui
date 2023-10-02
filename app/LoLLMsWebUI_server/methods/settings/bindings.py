from lollms.binding import BindingBuilder
from lollms.config import InstallOption
import gc
from lollms.helpers import ASCIIColors
from flask import jsonify, request


def reinstall_binding(self):
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return jsonify({"status":False, 'error':str(e)})
    ASCIIColors.info(f"- Reinstalling binding {data['name']}...")
    try:
        ASCIIColors.info("Unmounting binding and model")
        self.binding = None
        self.model = None
        for per in self.mounted_personalities:
            per.model = None
        gc.collect()
        ASCIIColors.info("Reinstalling binding")
        self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL)
        ASCIIColors.success("Binding reinstalled successfully")

        ASCIIColors.info("Please select a model")
        return jsonify({"status": True}) 
    except Exception as ex:
        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return jsonify({"status":False, 'error':str(ex)})

def unInstall_binding(self):
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return jsonify({"status":False, 'error':str(e)})
    ASCIIColors.info(f"- UnInstalling binding {data['name']}...")
    try:
        ASCIIColors.info("Unmounting binding and model")
        self.binding = None
        self.model = None
        for per in self.mounted_personalities:
            per.model = None
        gc.collect()
        ASCIIColors.info("UnInstalling binding")
        self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths, InstallOption.FORCE_INSTALL)
        self.binding.uninstall()
        ASCIIColors.success("Binding UnInstalled successfully")
        self.config.binding_name= None
        if self.config.auto_save:
            ASCIIColors.info("Saving configuration")
            self.config.save_config()
        ASCIIColors.info("Please select a binding")
        return jsonify({"status": True}) 
    except Exception as ex:
        ASCIIColors.error(f"Couldn't uninstall binding: [{ex}]")
        trace_exception(ex)
        return jsonify({"status":False, 'error':str(ex)})

def reload_binding(self):
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return jsonify({"status":False, 'error':str(e)})
    ASCIIColors.info(f"- Reloading binding {data['name']}...")
    try:
        ASCIIColors.info("Unmounting binding and model")
        self.binding = None
        self.model = None
        for personality in self.mounted_personalities:
            personality.model = None
        gc.collect()
        ASCIIColors.info("Reloading binding")
        self.binding =  BindingBuilder().build_binding(self.config, self.lollms_paths)
        ASCIIColors.info("Binding loaded successfully")

        try:
            ASCIIColors.info("Reloading model")
            self.model = self.binding.build_model()
            ASCIIColors.info("Model reloaded successfully")
        except Exception as ex:
            print(f"Couldn't build model: [{ex}]")
            trace_exception(ex)
        try:
            self.rebuild_personalities(reload_all=True)
        except Exception as ex:
            print(f"Couldn't reload personalities: [{ex}]")
        return jsonify({"status": True}) 
    except Exception as ex:
        ASCIIColors.error(f"Couldn't build binding: [{ex}]")
        trace_exception(ex)
        return jsonify({"status":False, 'error':str(ex)})
            

                

def get_active_binding_settings(self):
    print("- Retreiving binding settings")
    if self.binding is not None:
        if hasattr(self.binding,"binding_config"):
            return jsonify(self.binding.binding_config.config_template.template)
        else:
            return jsonify({})        
    else:
        return jsonify({})  
    

            


def set_active_binding_settings(self):
    print("- Setting binding settings")
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return
    
    if self.binding is not None:
        if hasattr(self.binding,"binding_config"):
            for entry in data:
                if entry["type"]=="list" and type(entry["value"])==str:
                    try:
                        v = json.loads(entry["value"])
                    except:
                        v= ""
                    if type(v)==list:
                        entry["value"] = v
                    else:
                        entry["value"] = [entry["value"]]
            self.binding.binding_config.update_template(data)
            self.binding.binding_config.config.save_config()
            self.binding = None
            self.model = None
            for per in self.mounted_personalities:
                per.model = None
            gc.collect()
            self.binding= BindingBuilder().build_binding(self.config, self.lollms_paths)
            self.model = self.binding.build_model()
            if self.config.auto_save:
                ASCIIColors.info("Saving configuration")
                self.config.save_config()
            return jsonify({'status':True})
        else:
            return jsonify({'status':False})        
    else:
        return jsonify({'status':False})