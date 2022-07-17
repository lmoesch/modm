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
    for d in env['PROTOCPATH']:
        d = env.GetBuildPath(d)
        if not os.path.isabs(d): d = os.path.relpath(d, prefix)
        include_dirs += ' -I' + esc(d)

    nanopb_flags = env['NANOPBFLAGS']
    if nanopb_flags:
      nanopb_flags = '--source-extension=%s,--header-extension=%s,%s:.' % (".cpp", ".hpp", nanopb_flags)
    else:
      nanopb_flags = '--source-extension=%s,--header-extension=%s:.' % (".cpp", ".hpp")

    return SCons.Action.CommandAction('python "$PROTOC" $PROTOCFLAGS %s --nanopb_out=blub %s %s' % (include_dirs, nanopb_flags, srcfile),
                                      chdir = prefix)

def _nanopb_proto_emitter(target, source, env):
    basename = os.path.splitext(str(source[0]))[0]
    source_extension = os.path.splitext(str(target[0]))[1]
    header_extension = '.h' + source_extension[2:]
    target.append(basename + '.pb' + header_extension)

    # This is a bit of a hack. protoc include paths work the sanest
    # when the working directory is the same as the source root directory.
    # To get that directory in _nanopb_proto_actions, we add SConscript to
    # the list of source files.

    if os.path.exists(basename + '.options'):
        source.append(basename + '.options')

    return target, source

_nanopb_proto_cpp_builder = SCons.Builder.Builder(
    generator = _nanopb_proto_actions,
    suffix = '.pb.cpp',
    src_suffix = '.proto',
    emitter = _nanopb_proto_emitter)

def blub(env, sources):
    env.Alias("nanopb", env.NanopbProtoCpp(sources))

def generate(env, **kw):    
    env['NANOPB'] = os.path.abspath(os.path.join("./", "ext/nanopb"))
    env['PROTOC'] = os.path.abspath(os.path.join("./ext/nanopb/", "generator", "protoc"))

    env.SetDefault(NANOPBFLAGS = '')
    env.SetDefault(PROTOCPATH = [".", os.path.join(env['NANOPB'], 'generator', 'proto')])

    env['BUILDERS']['NanopbProtoCpp'] = _nanopb_proto_cpp_builder

    env.AddMethod(blub, "BuildNanopbProto")

def exists(env):
	return True