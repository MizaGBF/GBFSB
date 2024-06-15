# GBF Sprite Builder  
  
A python script to parse Granblue Animation files and make Sprite sheets from them.  
  
# Disclamer  
- This is an old project.  
- Multiple versions of this project exist(ed).  
- It used to be obfuscated.  
  
As a result, what's presented here is condensed/best-of version, for educational and archival purpose.   
The code is quite awful to read. Only attempt to make use of it if you are really interested and extremely masochist.  
Additionally, being written in python, it's fairly slow. Add to this than it's making matrix calculus without using numpy or equivalent. This project was being used as a sort of pluging in many others and, as such, didn't want to rely on such third party libraries.  
  
### How-to  
The file includes an example.  
We'll follow it to give a rough explanation of how it works.  
  
```python
# EXAMPLE
async def example():
    from pathlib import Path # for folder creation
    target_id = 3040036000
    target_folder = str(target_id) + "/"

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=50)) as client:
        r = GBFSB(client)
        print("Loading element", target_id)
        await r.load(target_id, uncap=1, style='')
        if r.exist():
            Path(target_folder).mkdir(parents=True, exist_ok=True)
            print("Rendering CJS...")
            res = await r.renderCJS(build_dummy=True, build_sheet=1)
            for k in res['img']: # retrieve images
                with open(target_folder + k, "wb") as f:
                    f.write(res['img'][k])
            with open(target_folder + "dump.txt", mode="w", encoding="utf-8") as f: # retrieve dump
                f.write(res['dump'])
            print("Rendering NPC...")
            sp = await r.renderNPC(force_dummy=True)
            if sp is not None:
                with open(target_folder + "render.png", "wb") as f:
                    f.write(sp)
        else:
            print("No Positive Results")


if __name__ == "__main__":
    asyncio.run(example())
```
  
First, the project is reliant on asyncio, although it can easily be modified to be synchronous.  
Second, it requires an open aiohttp client to be passed.  
  
You can then create a GBFSB instance.  
```python
r = GBFSB(client)
```
To load an element, you pass it an id and an uncap. It also supports character styles.  
```python
await r.load(target_id, uncap=1, style='')
```
1 is the base uncap, 2 the one unlocked at 2 stars, 3 at FLB and 4 at ULB, at least for characters.  
The project supports characters, weapons and summons, although it can technically work with any animation from the game if you bothered to add it.  
This function searches for manifest files and take note of the spritesheet files which are supposed to be loaded.  
  
Next, you can call `exist` to check if the element is loaded and exists and then `renderCJS`.  
The later is where the magic happens.  
First, it accepts the following parameters:  
- `build_dummy`: A boolean, it must be set to True or it will only load the corresponding CJS files and parse them. Set it to False if you only want to use `renderNPC` below.  
- `build_sheet`: An integer. At 0, the feature is disabled. At 1, it create spritesheets from the animation files. At 2, it does the same as 1 but with transparency and without text and with smaller rectangles to be slower to actual character proportions. This mode is intended to be used with projects such as [GBFAP](https://github.com/MizaGBF/GBFAP) or [GBFBP](https://github.com/MizaGBF/GBFBP) for example. See the screenshots below for examples.  
- `bound_box`: A boolean. To be used when build_sheet is enabled. It draws green bound boxes instead.
  
![build_sheet 1](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_1.png?raw=true)
![build_sheet 2](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_2.png?raw=true)
![Demo in GBFBP with different colors](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_3.png?raw=true)
  
`renderCJS` returns a dictionary with two keys:  
- `dump`: A string value, which contains a dump of the full animation tree.  
- `img`: Another dictionary of pairs (string filename, PNG image as bytes).  
  
The following part of the example write those files to disk.  
  
Finally, the call to `renderNPC`. As the name indicates, it's only usable with characters, as the method used only work properly with them. It renders the first frame of the fade out animation as such:
  
![Render with bound boxes](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_4.png?raw=true)
  
It can also be used if spritesheets aren't available to have a breakdown of the character parts:
  
![Dummy Rendering](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_5.png?raw=true)
  
The function takes the following parameters:
- `enable_dummy`: Boolean, default True. Will attempt to render if spritesheets aren't available.  
- `enable_hitbox`: Boolean, default True. Add green bound boxes. Doesn't work in dummy mode.  
- `force_dummy`: Boolean, default False. Force dummy mode even if spritesheets are available.
  
This renderer has a defect:  
- It might render some elements intended for frames further in the animation. This is a problem noticeable with Wamdus' umbrella or Hekate's voluptous chest. The first has a hacky fix in place but not the second. More characters might be affected.  
- Shapes aren't supported. So particles and such won't appear on the output image.  