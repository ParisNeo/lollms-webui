# import subprocess


# def update_software(self):
#         ASCIIColors.info("")
#         ASCIIColors.info("")
#         ASCIIColors.info("")
#         ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
#         ASCIIColors.info(" ║               Upgrading backend                  ║")
#         ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
#         ASCIIColors.info("")
#         ASCIIColors.info("")
#         ASCIIColors.info("")        
#         # Perform a 'git pull' to check for updates
#         try:
#             # Execute 'git pull' and redirect the output to the console
#             process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

#             # Read and print the output in real-time
#             while True:
#                 output = process.stdout.readline()
#                 if output == '' and process.poll() is not None:
#                     break
#                 if output:
#                     print(output.strip())

#             # Wait for the process to finish and get the return code
#             return_code = process.poll()

#             if return_code == 0:
#                 return {"status": True}
#             else:
#                 return {"status": False, 'error': f"git pull failed with return code {return_code}"}
        
#         except subprocess.CalledProcessError as ex:
#             # There was an error in 'git pull' command
#             return {"status": False, 'error': str(ex)}

def check_update(self):
    if self.config.auto_update:
        res = check_update_()
        return jsonify({'update_availability':res})
    else:
        return jsonify({'update_availability':False})

def update_software(self):
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
    ASCIIColors.info(" ║                Updating backend                  ║")
    ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    run_update_script(self.args)

    