{
  description = "C/SDL2 graphical app for LLVM course exercises";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forSystems (pkgs:
        let llvm = pkgs.llvmPackages_21;
        in {
          default = (pkgs.mkShell.override { stdenv = llvm.stdenv; }) {
            packages = with pkgs; [
              cmake ninja pkg-config git SDL2 llvm.llvm
              (python3.withPackages (pythonPackages: [ pythonPackages.matplotlib ]))
            ];
            LLVM_DIR = "${llvm.llvm.dev}/lib/cmake/llvm";
          };
        });

      packages = forSystems (pkgs:
        let llvm = pkgs.llvmPackages_21;
        in {
          default = llvm.stdenv.mkDerivation {
            pname = "graphical-app";
            version = "0.1.0";
            src = self;
            nativeBuildInputs = with pkgs; [ cmake ninja pkg-config ];
            buildInputs = with pkgs; [ SDL2 llvm.llvm ];
            cmakeFlags = [ "-DLLVM_DIR=${llvm.llvm.dev}/lib/cmake/llvm" ];
            meta.mainProgram = "graphical_app";
          };
        });
    };
}
