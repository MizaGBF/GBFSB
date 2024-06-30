# GBF Sprite Builder  
  
A python script to parse Granblue Animation files and make Sprite sheets from them.  
  
# Disclamer  
- This is an old project.  
- Multiple versions of this project exist(ed), used as plugins for other projects.  
- It used to be obfuscated.  
- It was made to not use any external libraries (beside a HTTP client), so it's quite slow at making all the matrix transformations.  
- Improvement
  
To sum it up:  
What's presented here is condensed/best-of version, for educational and archival purpose.  
It had many design flaws and improvements are possible but I would rather rewrite it from the group up.  
  
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
            sp = await r.renderNPC()
            if sp is not None:
                with open(target_folder + "render.png", "wb") as f:
                    f.write(sp)
        else:
            print("No Positive Results")


if __name__ == "__main__":
    asyncio.run(example())
```
  
First, the project is reliant on asyncio, although it has been used in synchronous environments (with minimal modifications).  
Second, it requires a HTTP client to be passed to the instance. (In our use case, we use aiohttp)  
```python
r = GBFSB(client)
```
To set and load an element, you pass it an id and an uncap. It also supports character styles. You can only set one element per instance.  
```python
await r.load(target_id, uncap=1, style='')
```
1 is the base uncap, 2 the one unlocked at 2 stars, 3 at FLB and 4 at ULB, at least for characters.  
The project supports characters, weapons and summons, although it can technically work with ANY animation from the game if you bothered to add it.  
This function searches for manifest files and take note of the spritesheet files which are supposed to be loaded.  
  
Next, you can call `exist` to check if the element is loaded and exists, and then `renderCJS`.  
The later is where some of the magic happens.  
First, it accepts the following parameters:  
- `build_dummy`: A boolean, it must be set to True or it will only load the corresponding CJS files and parse them. Set it to False if you only want to use `renderNPC` (See below).  
- `build_sheet`: An integer. At 0, the feature is disabled. At 1, it creates spritesheets from the animation files. At 2, it does the same as 1 but with transparency and without text and with smaller rectangles to be closer to actual character proportions. This mode is intended to be used with projects such as [GBFAP](https://github.com/MizaGBF/GBFAP) or [GBFBP](https://github.com/MizaGBF/GBFBP) for example. See the screenshots below for examples.  
- `bound_box`: A boolean. To be used when build_sheet is enabled. It draws green bound boxes instead.  
- `normal_bound`: A boolean. If True and b`build_sheet` is set to 1, rectangles won't have a reduced sizes.  
  
Example 1: With build_sheet = 1.  
![example 1](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_1.png?raw=true)  
Example 2: With build_sheet = 2.  
![example 2](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_2.png?raw=true)  
Example 3: build_sheet = 2 in GBFBP with a different color palette.  
![example 3](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_GBFBP.png?raw=true)  
  
At its core, it access and read the CJS file corresponding to each manifest and parse it to build the following:  
- A list of sub rectangles, and their names, found in the "first half", which correspond to part of the spritesheets.  
- The animation tree of how every parts are rigged together.  
  
However, to keep things simple, it doesn't process any temporal data such as positions at X frames or the time passing between frames.  
  
`renderCJS` returns a dictionary with two keys:  
- `dump`: A string value, which contains a text dump of the full animation tree. Mostly for debug purpose.  
- `img`: Another dictionary of pairs (string filename and corresponding PNG image as bytes).  
  
The following part of the example write those files to disk.  
  
Finally, the call to `renderNPC`. As the name indicates, it's only usable with characters, as the method used only work properly with them. It renders the first frame of the fade out animation as such:
```python
sp = await r.renderNPC()
```
The returned value is a PNG image as bytes.  
  
Example 4: Render with enable_hitbox = True.  
![Render with bound boxes](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_4.png?raw=true)
  
It can also be used, in what I call dummy mode, to have a breakdown of the character parts (it doesn't require any spritesheets):
  
Example 5: Render in dummy mode.  
![Dummy Rendering](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_5.png?raw=true)
  
The function takes the following parameters:
- `enable_dummy`: Boolean, default True. Will attempt to render if spritesheets aren't available.  
- `enable_hitbox`: Boolean, default True. Add green bound boxes. Doesn't work in dummy mode.  
- `force_dummy`: Boolean, default False. Force dummy mode even if spritesheets are available.
  
This renderer has a few defects:  
- It might render some elements intended for frames further in the animation timeline. This is a problem noticeable with Wamdus' umbrella or Hekate's *voluptous* chest. The first has a hacky fix in place but not the second. More characters might be affected.  
- Shapes aren't supported. So particles and such won't appear on the output image.  
  
Fixing it would probably require a rewrite of the code to take into account the animation timeline.  
  
Example 6: Wamdus Renders without and with her fix.  
![Rendering Wamdus](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_6a.png?raw=true)  
You can see the variations of her umbrella overalapping.  
![Dummy Rendering Wamdus Fixed](https://github.com/MizaGBF/GBFSB/blob/main/assets/readme_example_6b.png?raw=true)  
With a small hack, only one shows up.  