{ pkgs ? import <nixpkgs> {}}:
let
  fhs = pkgs.buildFHSUserEnv {
    name = "my-fhs-environment";

    targetPkgs = _: with pkgs; [
      micromamba
      libGL
    ];

    profile = ''
      set -e
      eval "$(micromamba shell hook --shell=posix)"
      export MAMBA_ROOT_PREFIX=${builtins.getEnv "PWD"}/.mamba
      export MAMBA_ENV=cq
      if ! test -d $MAMBA_ROOT_PREFIX/envs/$MAMBA_ENV; then
          micromamba create --yes -q -n $MAMBA_ENV
      fi
      micromamba activate $MAMBA_ENV
      micromamba install --yes -f mamba_env.yaml -c conda-forge
      set +e
    '';
  };
in fhs.env

