from lollms.personality import AIPersonality
from lollms.config import InstallOption
import gc



def get_current_personality(self):
    return jsonify({"personality":self.personality.as_dict()})

def get_all_personalities(self):
    personalities_folder = self.lollms_paths.personalities_zoo_path
    personalities = {}

    for category_folder in  personalities_folder.iterdir():
        cat = category_folder.stem
        if category_folder.is_dir() and not category_folder.stem.startswith('.'):
            personalities[category_folder.name] = []
            for personality_folder in category_folder.iterdir():
                pers = personality_folder.stem
                if personality_folder.is_dir() and not personality_folder.stem.startswith('.'):
                    personality_info = {"folder":personality_folder.stem}
                    config_path = personality_folder / 'config.yaml'
                    if not config_path.exists():
                        """
                        try:
                            shutil.rmtree(str(config_path.parent))
                            ASCIIColors.warning(f"Deleted useless personality: {config_path.parent}")
                        except Exception as ex:
                            ASCIIColors.warning(f"Couldn't delete personality ({ex})")
                        """
                        continue                                    
                    try:
                        scripts_path = personality_folder / 'scripts'
                        personality_info['has_scripts'] = scripts_path.exists()
                        with open(config_path) as config_file:
                            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
                            personality_info['name'] = config_data.get('name',"No Name")
                            personality_info['description'] = config_data.get('personality_description',"")
                            personality_info['author'] = config_data.get('author', 'ParisNeo')
                            personality_info['version'] = config_data.get('version', '1.0.0')
                            personality_info['installed'] = (self.lollms_paths.personal_configuration_path/f"personality_{personality_folder.stem}.yaml").exists() or personality_info['has_scripts']
                            personality_info['help'] = config_data.get('help', '')
                            personality_info['commands'] = config_data.get('commands', '')

                        languages_path = personality_folder/ 'languages'

                        real_assets_path = personality_folder/ 'assets'
                        assets_path = Path("personalities") / cat / pers / 'assets'
                        gif_logo_path = assets_path / 'logo.gif'
                        webp_logo_path = assets_path / 'logo.webp'
                        png_logo_path = assets_path / 'logo.png'
                        jpg_logo_path = assets_path / 'logo.jpg'
                        jpeg_logo_path = assets_path / 'logo.jpeg'
                        svg_logo_path = assets_path / 'logo.svg'
                        bmp_logo_path = assets_path / 'logo.bmp'

                        gif_logo_path_ = real_assets_path / 'logo.gif'
                        webp_logo_path_ = real_assets_path / 'logo.webp'
                        png_logo_path_ = real_assets_path / 'logo.png'
                        jpg_logo_path_ = real_assets_path / 'logo.jpg'
                        jpeg_logo_path_ = real_assets_path / 'logo.jpeg'
                        svg_logo_path_ = real_assets_path / 'logo.svg'
                        bmp_logo_path_ = real_assets_path / 'logo.bmp'

                        if languages_path.exists():
                            personality_info['languages']=[f.stem for f in languages_path.iterdir() if f.suffix==".yaml"]
                        else:
                            personality_info['languages']=None
                            
                        personality_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
                        
                        if gif_logo_path_.exists():
                            personality_info['avatar'] = str(gif_logo_path).replace("\\","/")
                        elif webp_logo_path_.exists():
                            personality_info['avatar'] = str(webp_logo_path).replace("\\","/")
                        elif png_logo_path_.exists():
                            personality_info['avatar'] = str(png_logo_path).replace("\\","/")
                        elif jpg_logo_path_.exists():
                            personality_info['avatar'] = str(jpg_logo_path).replace("\\","/")
                        elif jpeg_logo_path_.exists():
                            personality_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
                        elif svg_logo_path_.exists():
                            personality_info['avatar'] = str(svg_logo_path).replace("\\","/")
                        elif bmp_logo_path_.exists():
                            personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
                        else:
                            personality_info['avatar'] = ""
                        
                        personalities[category_folder.name].append(personality_info)
                    except Exception as ex:
                        ASCIIColors.warning(f"Couldn't load personality from {personality_folder} [{ex}]")
                        trace_exception(ex)
    return json.dumps(personalities)

def get_personality(self):
    category = request.args.get('category')
    name = request.args.get('name')
    personality_folder = self.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"
    personality_path = personality_folder/f"config.yaml"
    personality_info = {}
    with open(personality_path) as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        personality_info['name'] = config_data.get('name',"unnamed")
        personality_info['description'] = config_data.get('personality_description',"")
        personality_info['author'] = config_data.get('creator', 'ParisNeo')
        personality_info['version'] = config_data.get('version', '1.0.0')
    scripts_path = personality_folder / 'scripts'
    personality_info['has_scripts'] = scripts_path.is_dir()
    assets_path = personality_folder / 'assets'
    gif_logo_path = assets_path / 'logo.gif'
    webp_logo_path = assets_path / 'logo.webp'
    png_logo_path = assets_path / 'logo.png'
    jpg_logo_path = assets_path / 'logo.jpg'
    jpeg_logo_path = assets_path / 'logo.jpeg'
    bmp_logo_path = assets_path / 'logo.bmp'
    
    personality_info['has_logo'] = png_logo_path.is_file() or gif_logo_path.is_file()
    
    if gif_logo_path.exists():
        personality_info['avatar'] = str(gif_logo_path).replace("\\","/")
    elif webp_logo_path.exists():
        personality_info['avatar'] = str(webp_logo_path).replace("\\","/")
    elif png_logo_path.exists():
        personality_info['avatar'] = str(png_logo_path).replace("\\","/")
    elif jpg_logo_path.exists():
        personality_info['avatar'] = str(jpg_logo_path).replace("\\","/")
    elif jpeg_logo_path.exists():
        personality_info['avatar'] = str(jpeg_logo_path).replace("\\","/")
    elif bmp_logo_path.exists():
        personality_info['avatar'] = str(bmp_logo_path).replace("\\","/")
    else:
        personality_info['avatar'] = ""
    return json.dumps(personality_info)

def get_current_personality_files_list(self):
    if self.personality is None:
        return jsonify({"state":False, "error":"No personality selected"})
    return jsonify({"state":True, "files":[{"name":Path(f).name, "size":Path(f).stat().st_size} for f in self.personality.files]})

def clear_personality_files_list(self):
    if self.personality is None:
        return jsonify({"state":False, "error":"No personality selected"})
    self.personality.remove_all_files()
    return jsonify({"state":True})

def p_mount_personality(self):
    print("- Mounting personality")
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return
    category = data['category']
    name = data['folder']

    language = data.get('language', None)

    package_path = f"{category}/{name}"
    package_full_path = self.lollms_paths.personalities_zoo_path/package_path
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        if language:
            package_path += ":" + language
        if package_path in self.config["personalities"]:
            ASCIIColors.error("Can't mount exact same personality twice")
            return jsonify({"status": False,
                            "error":"Can't mount exact same personality twice",
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })    
        self.config["personalities"].append(package_path)
        self.mounted_personalities = self.rebuild_personalities()
        self.config["active_personality_id"]= len(self.config["personalities"])-1
        self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        ASCIIColors.success("ok")
        if self.config["active_personality_id"]<0:
            return jsonify({"status": False,
                            "error":"active_personality_id<0",
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
        else:
            if self.config.auto_save:
                ASCIIColors.info("Saving configuration")
                self.config.save_config()
            return jsonify({"status": True,
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
    else:
        pth = str(config_file).replace('\\','/')
        ASCIIColors.error(f"nok : Personality not found @ {pth}")
        
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
        return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         



def p_remount_personality(self):
    print("- Remounting personality")
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return
    category = data['category']
    name = data['folder']




    package_path = f"{category}/{name}"
    package_full_path = self.lollms_paths.personalities_zoo_path/package_path
    config_file = package_full_path / "config.yaml"
    if config_file.exists():
        ASCIIColors.info(f"Unmounting personality {package_path}")
        index = self.config["personalities"].index(f"{category}/{name}")
        self.config["personalities"].remove(f"{category}/{name}")
        if self.config["active_personality_id"]>=index:
            self.config["active_personality_id"]=0
        if len(self.config["personalities"])>0:
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        else:
            self.personalities = ["generic/lollms"]
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]


        ASCIIColors.info(f"Mounting personality {package_path}")
        self.config["personalities"].append(package_path)
        self.mounted_personalities = self.rebuild_personalities()
        self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        ASCIIColors.success("ok")
        if self.config["active_personality_id"]<0:
            return jsonify({"status": False,
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
        else:
            return jsonify({"status": True,
                            "personalities":self.config["personalities"],
                            "active_personality_id":self.config["active_personality_id"]
                            })         
    else:
        pth = str(config_file).replace('\\','/')
        ASCIIColors.error(f"nok : Personality not found @ {pth}")
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
        return jsonify({"status": False, "error":f"Personality not found @ {pth}"})         

def p_unmount_personality(self):
    print("- Unmounting personality ...")
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return
    category    = data['category']
    name        = data['folder']
    language    = data.get('language',None)
    try:
        personality_id = f"{category}/{name}" if language is None else f"{category}/{name}:{language}"
        index = self.config["personalities"].index(personality_id)
        self.config["personalities"].remove(personality_id)
        if self.config["active_personality_id"]>=index:
            self.config["active_personality_id"]=0
        if len(self.config["personalities"])>0:
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        else:
            self.personalities = ["generic/lollms"]
            self.mounted_personalities = self.rebuild_personalities()
            self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        ASCIIColors.success("ok")
        if self.config.auto_save:
            ASCIIColors.info("Saving configuration")
            self.config.save_config()
        return jsonify({
                    "status": True,
                    "personalities":self.config["personalities"],
                    "active_personality_id":self.config["active_personality_id"]
                    })         
    except:
        if language:
            ASCIIColors.error(f"nok : Personality not found @ {category}/{name}:{language}")
        else:
            ASCIIColors.error(f"nok : Personality not found @ {category}/{name}")
            
        ASCIIColors.yellow(f"Available personalities: {[p.name for p in self.mounted_personalities]}")
        return jsonify({"status": False, "error":"Couldn't unmount personality"})         
        
def get_active_personality_settings(self):
    print("- Retreiving personality settings")
    if self.personality.processor is not None:
        if hasattr(self.personality.processor,"personality_config"):
            return jsonify(self.personality.processor.personality_config.config_template.template)
        else:
            return jsonify({})        
    else:
        return jsonify({})

def set_active_personality_settings(self):
        print("- Setting personality settings")
        try:
            data = request.get_json()
            # Further processing of the data
        except Exception as e:
            print(f"Error occurred while parsing JSON: {e}")
            return
        
        if self.personality.processor is not None:
            if hasattr(self.personality.processor,"personality_config"):
                self.personality.processor.personality_config.update_template(data)
                self.personality.processor.personality_config.config.save_config()
                if self.config.auto_save:
                    ASCIIColors.info("Saving configuration")
                    self.config.save_config()
                return jsonify({'status':True})
            else:
                return jsonify({'status':False})        
        else:
            return jsonify({'status':False}) 

def get_personality_settings(self):
    print("- Retreiving personality settings")
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return
    category = data['category']
    name = data['folder']

    if category.startswith("personal"):
        personality_folder = self.lollms_paths.personal_personalities_path/f"{category}"/f"{name}"
    else:
        personality_folder = self.lollms_paths.personalities_zoo_path/f"{category}"/f"{name}"

    personality = AIPersonality(personality_folder,
                                self.lollms_paths, 
                                self.config,
                                model=self.model,
                                app=self,
                                run_scripts=True)
    if personality.processor is not None:
        if hasattr(personality.processor,"personality_config"):
            return jsonify(personality.processor.personality_config.config_template.template)
        else:
            return jsonify({})        
    else:
        return jsonify({})       


def p_select_personality(self):

    data = request.get_json()
    id = data['id']
    print(f"- Selecting active personality {id} ...",end="")
    if id<len(self.mounted_personalities):
        self.config["active_personality_id"]=id
        self.personality = self.mounted_personalities[self.config["active_personality_id"]]
        ASCIIColors.success("ok")
        print(f"Mounted {self.personality.name}")
        if self.config.auto_save:
            ASCIIColors.info("Saving configuration")
            self.config.save_config()
        return jsonify({
            "status": True,
            "personalities":self.config["personalities"],
            "active_personality_id":self.config["active_personality_id"]                
            })
    else:
        ASCIIColors.error(f"nok : personality id out of bounds @ {id} >= {len(self.mounted_personalities)}")
        return jsonify({"status": False, "error":"Invalid ID"})

def get_current_personality_path_infos(self):
    if self.personality is None:
        return jsonify({
            "personality_category":"", 
            "personality_name":""
        })
    else:
        return jsonify({
            "personality_category":self.personality_category, 
            "personality_name":self.personality_name
        })

def delete_personality(self):
    category = request.args.get('category')
    name = request.args.get('name')
    path = Path("personalities")/category/name
    try:
        shutil.rmtree(path)
        return jsonify({'status':True})
    except Exception as ex:
        return jsonify({'status':False,'error':str(ex)})

def reinstall_personality(self):
    try:
        data = request.get_json()
        # Further processing of the data
    except Exception as e:
        print(f"Error occurred while parsing JSON: {e}")
        return jsonify({"status":False, 'error':str(e)})
    if not 'name' in data:
        data['name']=self.config.personalities[self.config["active_personality_id"]]
    try:
        personality_path = lollms_paths.personalities_zoo_path / data['name']
        ASCIIColors.info(f"- Reinstalling personality {data['name']}...")
        ASCIIColors.info("Unmounting personality")
        idx = self.config.personalities.index(data['name'])
        print(f"index = {idx}")
        self.mounted_personalities[idx] = None
        gc.collect()
        try:
            self.mounted_personalities[idx] = AIPersonality(personality_path,
                                        self.lollms_paths, 
                                        self.config,
                                        model=self.model,
                                        app=self,
                                        run_scripts=True,installation_option=InstallOption.FORCE_INSTALL)
            return jsonify({"status":True})
        except Exception as ex:
            ASCIIColors.error(f"Personality file not found or is corrupted ({data['name']}).\nReturned the following exception:{ex}\nPlease verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
            ASCIIColors.info("Trying to force reinstall")
            return jsonify({"status":False, 'error':str(e)})

    except Exception as e:
        return jsonify({"status":False, 'error':str(e)})

def post_to_personality(self):
    data = request.get_json()
    if hasattr(self.personality.processor,'handle_request'):
        return self.personality.processor.handle_request(data)
    else:
        return jsonify({})