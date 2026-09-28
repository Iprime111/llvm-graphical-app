{
  description = "C/SDL2 graphical app for LLVM course exercises";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [ clang cmake ninja pkg-config git SDL2 ];
        };
      });

      packages = forSystems (pkgs: {
        default = pkgs.stdenv.mkDerivation {
          pname = "graphical-app";
          version = "0.1.0";
          src = self;
          nativeBuildInputs = with pkgs; [ clang cmake ninja pkg-config ];
          buildInputs = with pkgs; [ SDL2 ];
          meta.mainProgram = "graphical_app";
        };
      });
    };
}
