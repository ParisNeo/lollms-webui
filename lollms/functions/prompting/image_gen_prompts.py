# Lollms function call definition file
# File Name: get_random_image_gen_prompt.py
# Author: ParisNeo
# Description: This function returns a random image_gen prompt for various instructional roles. Each prompt includes a title and content that describes the role and its mission.

# Import necessary libraries
import random
from typing import Tuple, List, Dict, Any
from safe_store import SafeStore
# ascii_colors offers advanced console coloring and bug tracing
from ascii_colors import trace_exception

def get_prompts_list():
    """
    Returns a list of prompts. These prompts have been generated using AI through a well structured prompting gained from experiments and searches from the internet.

    """
    return [
        "abstract image, Bauhaus style, 3D, phages, black, white, red and blue, 8K",
        "abstract artwork, Bauhaus style, 3D, viruses, black, white, red and blue, 8K",
        "modern abstract, Bauhaus style, 3D, bacteriophages, black, white, red and blue, 8K",
        "geometric abstract, Bauhaus style, 3D, phages, monochrome with red and blue accents, 8K",
        "abstract composition, Bauhaus style, 3D, phages, black, white, red and blue, high resolution",
        "abstract design, Bauhaus style, 3D, phages, black, white, red and blue, ultra HD",
        "abstract scene, Bauhaus style, 3D, phages, black, white, red and blue, 8K resolution",
        "abstract visual, Bauhaus style, 3D, phages, black, white, red and blue, 8K quality",
        "abstract pattern, Bauhaus style, 3D, phages, black, white, red and blue, 8K definition",
        "abstract graphic, Bauhaus style, 3D, phages, black, white, red and blue, 8K clarity",
        "Extreme close up of an eye that is the mirror of the nostalgic moments, nostalgia expression, sad emotion, tears, made with imagination, detailed, photography, 8k, printed on Moab Entrada Bright White Rag 300gsm, Leica M6 TTL, Leica 75mm 2.0 Summicron-M ASPH, Cinestill 800T",
        "Extreme close up of a hand holding a vintage locket, symbolizing lost love, emotional expression, detailed, photography, 8k, printed on Hahnemühle Photo Rag 308gsm, Canon EOS R5, Canon RF 85mm F1.2L USM, Kodak Portra 400",
        "Extreme close up of a child's face with a single tear, representing innocence and loss, emotional expression, detailed, photography, 8k, printed on Ilford Galerie Prestige Gold Fibre Silk 310gsm, Nikon Z7, Nikkor Z 50mm f/1.8 S, Fujifilm Pro 400H",
        "Extreme close up of an old photograph in a hand, symbolizing memories and time, nostalgic expression, detailed, photography, 8k, printed on Canson Infinity Platine Fibre Rag 310gsm, Sony A7R IV, Sony FE 90mm f/2.8 Macro G OSS, Ilford HP5 Plus",
        "Extreme close up of a tear rolling down a cheek, capturing sorrow and reflection, emotional expression, detailed, photography, 8k, printed on Epson Hot Press Bright 330gsm, Fujifilm GFX 100, Fujinon GF 110mm f/2 R LM WR, Kodak Ektar 100",
        "Extreme close up of a wrinkled hand holding a faded letter, symbolizing time and memories, nostalgic expression, detailed, photography, 8k, printed on Moab Juniper Baryta Rag 305gsm, Leica SL2, Leica APO-Summicron-SL 75mm f/2 ASPH, Cinestill 50D",
        "Extreme close up of an eye reflecting a distant memory, capturing longing and sadness, emotional expression, detailed, photography, 8k, printed on Hahnemühle FineArt Baryta 325gsm, Canon EOS R3, Canon RF 50mm F1.2L USM, Kodak Tri-X 400",
        "Extreme close up of a tear-streaked face, symbolizing heartbreak and nostalgia, emotional expression, detailed, photography, 8k, printed on Ilford Galerie Smooth Pearl 310gsm, Nikon D850, Nikkor 85mm f/1.4G, Fujifilm Velvia 50",
        "Extreme close up of a vintage watch in a hand, representing the passage of time, nostalgic expression, detailed, photography, 8k, printed on Canson Infinity Baryta Photographique 310gsm, Sony A1, Sony FE 135mm f/1.8 GM, Kodak Gold 200",
        "Extreme close up of an eye with a tear, capturing deep sorrow and reflection, emotional expression, detailed, photography, 8k, printed on Epson Legacy Platine 314gsm, Fujifilm X-T4, Fujinon XF 56mm f/1.2 R, Ilford Delta 3200",
        "Extreme close up of an eye that is the mirror of the nostalgic moments, nostalgia expression, sad emotion, tears, made with imagination, detailed, photography, 8k, printed on Moab Entrada Bright White Rag 300gsm, Leica M6 TTL, Leica 75mm 2.0 Summicron-M ASPH, Cinestill 800T",
        "Portrait of a handsome man with dark hair, wearing a tailored suit, a city skyline at dusk, blue and silver color scheme.",
        "Portrait of a young girl with curly red hair, wearing a fairy costume with wings, a magical forest scene, pastel and glitter color scheme.",
        "Portrait of an elderly man with a white beard, wearing a traditional robe, a mountain landscape at sunrise, earthy and warm color scheme.",
        "Portrait of a teenage boy with glasses, holding a book, a library background, muted and academic color scheme.",
        "Portrait of a woman with short black hair, wearing a futuristic outfit, a sci-fi cityscape, neon and metallic color scheme.",
        "Portrait of a young woman with braids, wearing a traditional African dress, a savannah scene, vibrant and earthy color scheme.",
        "Portrait of a man with a rugged look, wearing a leather jacket, a desert scene at sunset, brown and orange color scheme.",
        "Portrait of a woman with long wavy hair, wearing a bohemian outfit, a beach scene at sunrise, turquoise and sandy color scheme.",
        "Portrait of a young boy with a mischievous smile, wearing a pirate costume, a treasure island scene, bold and adventurous color scheme.",
        "Portrait of a woman with a serene expression, wearing a yoga outfit, a zen garden scene, green and white color scheme.",
        "Photorealistic, visionary portrait of a young woman with a serene expression, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, soft gaze, rendered in pastel tones, evoking Vermeer, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a middle-aged man with a rugged look, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, intense gaze, rendered in monochrome, evoking Ansel Adams, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a young boy with a mischievous smile, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, playful gaze, rendered in vibrant colors, evoking Norman Rockwell, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of an elderly woman with kind eyes, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, gentle gaze, rendered in warm sepia tones, evoking Dorothea Lange, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a young girl with curly hair, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, curious gaze, rendered in soft pastel tones, evoking Mary Cassatt, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a middle-aged woman with a determined expression, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, focused gaze, rendered in cool tones, evoking Edward Hopper, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a young man with a confident look, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, steady gaze, rendered in bold colors, evoking Diego Rivera, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of an elderly man with a wise expression, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, thoughtful gaze, rendered in muted tones, evoking Andrew Wyeth, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a young woman with a joyful smile, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, bright gaze, rendered in vibrant hues, evoking Frida Kahlo, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Photorealistic, visionary portrait of a middle-aged man with a contemplative look, digitally enhanced, high contrast, chiaroscuro lighting technique, intimate, close-up, detailed, pensive gaze, rendered in deep shadows, evoking Caravaggio, timeless, expressive, highly detailed, sharp focus, high resolution.",
        "Closeup portrait photo of a handsome goth man, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a young goth girl, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of an elderly goth woman, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a teenage goth boy, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth woman with short hair, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth man with long hair, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth woman with piercings, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth man with tattoos, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth woman with a mysterious expression, makeup, 8k UHD, high quality, dramatic, cinematic.",
        "Closeup portrait photo of a goth man with a serious look, makeup, 8k UHD, high quality, dramatic, cinematic.",            
        "Close up photo of a squirrel, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a deer, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a fox, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a bird, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a hedgehog, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a butterfly, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a frog, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a snail, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a chipmunk, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Close up photo of a fawn, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot.",
        "Breathtaking shot of a watch, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a pair of shoes, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a perfume bottle, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a necklace, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a car, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a smartphone, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a dress, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a pair of sunglasses, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a bottle of wine, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Breathtaking shot of a pen, luxury product style, elegant, sophisticated, high-end, luxurious, professional, highly detailed.",
        "Johnny Depp photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Audrey Hepburn photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Humphrey Bogart photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Lauren Bacall photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "James Cagney photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Rita Hayworth photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Orson Welles photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Ingrid Bergman photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Clark Gable photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "Veronica Lake photo portrait, film noir style, monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic.",
        "A dog under the snow with brown eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A fox under the snow with green eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A rabbit under the snow with black eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A wolf under the snow with yellow eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A deer under the snow with gentle eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A squirrel under the snow with curious eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "An owl under the snow with piercing eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A bear under the snow with calm eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A raccoon under the snow with mischievous eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "A horse under the snow with soulful eyes, covered by snow, cinematic style, medium shot, professional photo, animal.",
        "Cartoonish depiction of King Nimrod on an exaggerated golden throne, surrounded by comically oversized palace guards, vibrant colors, exaggerated facial features, Babylonian-inspired architecture in background, whimsical art style, bold outlines, flat shading, exaggerated proportions, playful details, animated expression, 2D stylized artwork, Disney-esque character design, ornate patterns on clothing and decorations.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk street environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk nightclub environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk alleyway environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk subway station environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk rooftop garden environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk bridge environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk shopping district environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk park environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk office environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "A glamorous digital magazine photoshoot, a fashionable model wearing avant-garde clothing, set in a futuristic cyberpunk penthouse environment, with a neon-lit city background, intricate high fashion details, backlit by vibrant city glow, Vogue fashion photography.",
        "Freshly made hot herbal tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot green tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot black tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot chamomile tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot peppermint tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot ginger tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot lemon tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot rooibos tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot oolong tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Freshly made hot jasmine tea in glass kettle on the table, angled shot, midday warm, Nikon D850 105mm, close-up.",
        "Symbol of a stylized pink dog head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink fox head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink rabbit head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink owl head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink bear head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink lion head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink tiger head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink wolf head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink dragon head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "Symbol of a stylized pink unicorn head with sunglasses, glowing, neon, logo for a game, cyberpunk, vector, dark background with black and blue abstract shadows, cartoon, simple.",
        "A boy sitting in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A woman sitting in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A man sitting in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A couple sitting in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A group of friends sitting in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A barista serving coffee in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A girl reading a book in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A girl working on a laptop in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A girl drawing in a sketchbook in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "A girl talking on the phone in the cafe, comic, graphic illustration, comic art, graphic novel art, vibrant, highly detailed, colored, 2D minimalistic.",
        "Haunted mansion, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Spooky forest, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Ghostly graveyard, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Creepy castle, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Abandoned asylum, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Eerie lighthouse, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Mystical swamp, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Dark cave, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Haunted carnival, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Witch's hut, pixel-art, low-res, blocky, pixel art style, 8-bit graphics, colorful.",
        "Superman, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Wonder Woman, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Spider-Man, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Iron Man, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Captain America, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Thor, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Hulk, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Black Panther, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Aquaman, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Flash, cute modern Disney style, Pixar 3D portrait, ultra detailed, gorgeous, 3D ZBrush, trending on Dribbble, 8K render.",
        "Croissant on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Muffin on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Cupcake on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Donut on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Scone on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Bagel on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Pancake stack on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Waffle on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "French toast on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "Apple pie slice on the plate, watercolor painting, detailed, brush strokes, light palette, light, cozy.",
        "A boy astronaut exploring the cosmos, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A woman astronaut exploring the cosmos, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A man astronaut exploring the cosmos, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A couple of astronauts exploring the cosmos, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A group of astronauts exploring the cosmos, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A girl astronaut discovering a new planet, floating among stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A girl astronaut meeting an alien, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A girl astronaut in a space station, looking out at the cosmos, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A girl astronaut with a space pet, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "A girl astronaut repairing a spaceship, floating among planets and stars, high quality detail, anime screencap, Studio Ghibli style, illustration, high contrast, masterpiece, best quality.",
        "Double exposure portrait of a handsome man with black hair and a snowy tree under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with blonde hair and a snowy tree under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with red hair and a snowy tree under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with black hair and a snowy tree under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy forest under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy mountain under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy landscape under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy cityscape under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy village under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Double exposure portrait of a beautiful woman with brown hair and a snowy river under the bright moonlight by Dave White, Conrad Roset, Brandon Kidwell, Andreas Lie, Dan Mountford, Agnes Cecile, splash art, winter colours, gouache, triadic colours, thick opaque strokes, brocade, depth of field, hyperdetailed, whimsical, amazing depth, dynamic, dreamy masterwork.",
        "Boy with blue hair, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Woman with purple hair, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Man with green hair, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and sunglasses, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a futuristic outfit, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a neon cityscape background, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a hoverboard, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a neon-lit arcade, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a cyberpunk helmet, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "Girl with pink hair and a neon-lit street, vaporwave style, retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed.",
        "A tiger, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A wolf, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A bear, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "An eagle, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A fox, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A dragon, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A unicorn, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A phoenix, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A deer, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "A cheetah, colorful, low-poly, cyan and orange eyes, poly-hd, 3d, low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition.",
        "Vibrant and dynamic die cut sticker design, portraying a lion's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a tiger's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a bear's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying an eagle's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a fox's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a dragon's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a unicorn's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a phoenix's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a deer's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Vibrant and dynamic die cut sticker design, portraying a cheetah's head interlaced with cosmic galaxies, AI, stickers, high contrast, bright neon colors, top-view, high resolution, vector art, detailed stylization, modern graphic art, unique, opaque, weather resistant, UV laminated, white background.",
        "Logo of a mountain, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain peak, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain range, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a hiker, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a sunrise, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a trail, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with trees, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a river, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a tent, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a mountain with a compass, hike, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a coffee cup, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a book, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a bicycle, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a camera, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a music note, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a tree, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a rocket, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a heart, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a light bulb, modern, colorful, rounded, 2D concept, white off background.",
        "Logo of a globe, modern, colorful, rounded, 2D concept, white off background.",
        "A guitar, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "An acoustic guitar, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "An electric guitar, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A bass guitar, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A classical guitar, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A ukulele, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A guitar pick, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A guitar headstock, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A guitar amplifier, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A guitar pedal, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A laptop, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A smartphone, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A tablet, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A smartwatch, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A camera, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A pair of headphones, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A microphone, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A printer, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A drone, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A game controller, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A light bulb, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A book, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A coffee cup, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A bicycle, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A car, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A house, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A tree, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A mountain, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A globe, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A heart, 2D minimalistic icon, flat vector illustration, digital, smooth shadows, design asset.",
        "A tattoo design of a small bird, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small sparrow, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small hummingbird, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small swallow, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small robin, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small finch, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small wren, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small chickadee, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small bluebird, minimalistic, black and white drawing, detailed, 8K resolution.",
        "A tattoo design of a small canary, minimalistic, black and white drawing, detailed, 8K resolution.",
        "Ethereal fantasy concept art of an elf, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf queen, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf warrior, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf mage, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf archer, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf princess, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf druid, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf sorceress, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf bard, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy.",
        "Ethereal fantasy concept art of an elf ranger, magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy."        

    ]

def get_random_image_gen_prompt(number_of_examples: int = 1) -> List[Tuple[str, str]]:
    """
    Returns a list of random image_gen prompts for various instructional roles.

    Each prompt includes a title and content that describes the role and its mission.
    
    Args:
        number_of_examples (int): The number of random examples to return. Defaults to 1.
    
    Returns:
        List[Tuple[str, str]]: A list of tuples containing the title and content of the image_gen prompts.
    """
    try:
        prompts_list = get_prompts_list()
        if number_of_examples > len(prompts_list):
            raise ValueError("Requested number of examples exceeds the available prompts.")
        
        return random.sample(prompts_list, number_of_examples)
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    except Exception as e:
        return trace_exception(e)


def get_image_gen_prompt(agent_name, number_of_entries=5) -> Tuple[str, str]:
    """
    Returns a random image_gen prompt for various instructional roles.

    Each prompt includes a title and content that describes the role and its mission.
    
    Returns:
        Tuple[str, str]: A tuple containing the title and content of the image_gen prompt.
    """
    try:
        db = SafeStore("")

        image_gen_prompts = get_prompts_list()
        for entry in image_gen_prompts:
            db.add_text(entry[0], entry[0])
        results = db.query(agent_name, number_of_entries)

        return [(r["content"],image_gen_prompts[image_gen_prompts.index(r["content"])]) for r in results]
    except Exception as e:
        return trace_exception(e)

# Metadata function
def get_random_image_gen_prompt_function() -> Dict[str, Any]:
    """
    Returns metadata for the get_random_image_gen_prompt function.

    Returns:
        Dict[str, Any]: Metadata including function name, function itself, description, and parameters.
    """
    return {
        "function_name": "get_random_image_gen_prompt",
        "function": get_random_image_gen_prompt,
        "function_description": "Returns a random image_gen prompt for various instructional roles.",
        "function_parameters": []  # No parameters needed for this function
    }
