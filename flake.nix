{
  description = "Nix flake environment for a sample Python project scaffolding for Machine Learning";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/release-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self , flake-utils , nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
    let
        pkgs = import nixpkgs { inherit system; };
    in
    rec {

        devShells.default = pkgs.mkShell {
           venvDir = "./.venv";
           buildInputs = with pkgs; [
               pkgs.python310Packages.python
               pkgs.python310Packages.venvShellHook
               pkgs.ffmpeg
               pkgs.black
               # this is how we add native dependencies to the shell
               # e.g. grpc libstdc++.so.6
               stdenv.cc.cc.lib
           ];

          postVenvCreation = ''
            unset SOURCE_DATE_EPOCH
            pip install -r requirements.txt --editable .
          '';

          # Now we can execute any commands within the virtual environment.
          # This is optional and can be left out to run pip manually.
          postShellHook = ''
            # allow pip to install wheels
            echo "LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib" >> .venv/bin/activate
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib 
            unset SOURCE_DATE_EPOCH
          '';
       };
    });
}
