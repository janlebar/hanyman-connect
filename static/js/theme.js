            if (document.getElementById('nav-mobile-btn')) {
                document.getElementById('nav-mobile-btn').addEventListener('click', function () {
                    if (this.classList.contains('close')) {
                        document.getElementById('nav').classList.add('hidden');
                        this.classList.remove('close');
                    } else {
                        document.getElementById('nav').classList.remove('hidden');
                        this.classList.add('close');
                    }
                });
            }

            function theme() {
                var element = document.body;
                element.classList.toggle("dark");
                // prevent img flip
                var elements = document.getElementsByTagName("img");
                for (let index = 0; index < elements.length; index++) {
                    const element = elements[index];
                    element.classList.toggle("flip");
                }
                // toggle button
                var img1 = "https://www.nicepng.com/png/full/121-1215503_sun-icon-white-sun-blue-background.png",
                    img2 = "https://img.icons8.com/ios-glyphs/30/000000/moon-symbol.png";
                var imgElement = document.getElementById('theme-switch');
                imgElement.src = (imgElement.src === img1) ? img2 : img1;
            };
