#coding:utf-8
# Author @patriciogv - 2015
# http://patricio.io

import sublime
import sublime_plugin

import os
import subprocess

version = "0.5.0"

def haveExt(_file,_extentions):
    rta = False
    if isinstance(_extentions, list):
        for ext in _extentions:
            if os.path.splitext(_file)[1] == ext:
                rta = True
                break
    else:
        rta = os.path.splitext(_file)[1] == _extentions
    return rta

def OpenShader(view):
    shaderFile = view.file_name()
    settings = sublime.load_settings('glslViewer.sublime-settings')
    if settings.get('auto-start'):
        if haveExt(shaderFile, '.frag'):
            cmd = []
            cmd.append(settings.get('path')+'glslViewer')
            # cmd.append(shaderFile)
            os.chdir(os.path.dirname(shaderFile))
            os.system('taskkill /F /IM "glslViewer.exe"')   #kill the orign process

            basename = os.path.basename(shaderFile)
            images = []

            for elementOnDir in os.listdir('.'):
                file = os.path.basename(elementOnDir)
                if os.path.splitext(basename)[0] == os.path.splitext(file)[0]:
                    if haveExt(file, ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG']):
                        images.append(file)
                    if haveExt(file, ['.frag','.fs','.vert','.vs','.ply','.obj']):
                        cmd.append(file)

            nTextures = len(view.find_all('uniform sampler2D'))
            if nTextures == 1 and len(images) == 1:
                cmd.append(images[0])
                subprocess.Popen(cmd)
                # sublime.active_window().run_command('exec',{'cmd':cmd})
            elif nTextures > 0:
                fp = open(shaderFile)
                textures = []
                for file in os.listdir('.'):
                    if haveExt(file, ['.jpg','.JPG','.png','.PNG']):
                        images.append(file)
                    if len(images) >= nTextures:
                        break;
                images.append("*.png")
                while 1:
                    line = fp.readline()
                    if not line:
                        break
                    result = re.search(r'(uniform)\s+(sampler2D)\s+(\w*)', line)
                    if result != None:
                        textures.append(result.group(3))
                def askForTexture(i):
                    def done(filename):
                        cmd.append('--'+textures[i])
                        cmd.append(os.path.abspath(filename))
                        if textures[i] == textures[-1]:
                            subprocess.Popen(cmd)
                            # sublime.active_window().run_command('exec',{'cmd':cmd})
                        else:
                            askForTexture(i+1)
                    def cancel():
                        return

                    sublime.active_window().show_input_panel("Load "+textures[i]+" width: ", images[i % len(images)], done, None, cancel)

                askForTexture(0)
            else:
                subprocess.Popen(cmd)
                # sublime.active_window().run_command('exec',{'cmd':cmd})

class GlslViewerCommand(sublime_plugin.EventListener):
    def on_load(self,view):
        OpenShader(view)

class OpenShaderCommand(sublime_plugin.WindowCommand):
    def run(self):
        OpenShader(self.window.active_view())

class GlslTemplateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "\
#ifdef GL_ES\n\
precision mediump float;\n\
#endif\n\
\n\
uniform float u_time;\n\
uniform vec2 u_mouse;\n\
uniform vec2 u_resolution;\n\
\n\
void main (void) {\n\
    vec2 st = gl_FragCoord.xy/u_resolution.xy;\n\
    vec3 color = vec3(st,0.0);\n\
\n\
\n\
    gl_FragColor = vec4(color,1.0);\n\
}\n")


#to meet the shader toy
class InsertShaderToyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        text = "\n\
#define iResolution u_resolution\n\
#define iGlobalTime u_time\n\
#define iMouse u_mouse\n\
#define iChannel0 u_tex0\n\
"
        for region in self.view.sel():
            if region.empty():
                line = self.view.line(region)
                self.view.insert(edit, line.end(), text)
            else:
                self.view.insert(edit, region.end(), text)

class NewShaderCommand(sublime_plugin.WindowCommand):
    def run(self):
        newView = self.window.new_file()
        newView.run_command('glsl_template')
