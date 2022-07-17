import SCons.Action
import SCons.Builder
import SCons.Util
from SCons.Script import Dir, File

import os.path
import platform
import sys

def _nanopb_proto_actions(source, target, env, for_signature):
    esc = env['ESCAPE']

    prefix = os.path.dirname(str(source[-1]))
    srcfile = esc(os.path.relpath(str(source[0]), prefix))
    include_dirs = '-I.'

    nanopb_flags = env['NANOPBFLAGS']
    # if nanopb_flags:
    #   nanopb_flags = '--source-extension=%s,--header-extension=%s,%s:.' % (".cpp", ".hpp", nanopb_flags)
    # else:
    #   nanopb_flags = '--source-extension=%s,--header-extension=%s:.' % (".cpp", ".hpp")

    return SCons.Action.CommandAction('python "$PROTOC" $PROTOCFLAGS %s --nanopb_out=. %s %s' % (include_dirs, nanopb_flags, srcfile),
                                      chdir = prefix)

def _nanopb_proto_emitter(target, source, env):
    basename = os.path.splitext(str(source[0]))[0]
    source_extension = os.path.splitext(str(target[0]))[1]
    header_extension = '.h' + source_extension[2:]
    target.append(basename + '.pb' + header_extension)

    # if os.path.exists(basename + '.options'):
    #     source.append(basename + '.options')

    return target, source

_nanopb_proto_cpp_builder = SCons.Builder.Builder(
    generator = _nanopb_proto_actions,
    suffix = '.pb.c',
    src_suffix = '.proto',
    emitter = _nanopb_proto_emitter)

def build_proto(env, sources):
    env.Alias("nanopb", env.NanopbProtoCpp(sources))
    env.Default("nanopb")

def generate(env, **kw):    
    env['NANOPB'] = os.path.abspath(os.path.join("./", "ext/nanopb"))
    env['PROTOC'] = os.path.abspath(os.path.join("./ext/nanopb/", "generator", "protoc"))

    env.SetDefault(NANOPBFLAGS = '')
    env.SetDefault(PROTOCPATH = [".", os.path.join(env['NANOPB'], 'generator', 'proto')])

    env['BUILDERS']['NanopbProtoCpp'] = _nanopb_proto_cpp_builder

    env.AddMethod(build_proto, "BuildNanopbProto")

def exists(env):
	return True