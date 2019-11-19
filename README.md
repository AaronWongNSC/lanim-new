# lanim-new
 LaTeX Animation Script

## Introduction

This repository is a combination of me experimenting with GitHub and posting the LaTeX animation script that I've been developing. I have no idea how long I'm going to stick with this, but as long as I'm playing around with stuff, I will try my best to keep this going.

Basically, this exist because I wanted to make mathematical animations. But I didn't want to pay to learn animation software to do it. I tried to learn Blender, but that was mostly incomprehensible. I do have friends that know how to use the Adobe suite to do this sort of thing, but I didn't want to have to pay the fee for something I would only use sporadically.

But I know how to use TikZ in LaTeX. And I know how to program. And so I wanted to bring those two skills together to help me reach my joint goals of making animations and not spending money. And this is the result.

## Workflow Basics

Here is the workflow that I use with this script. It's all free stuff and a lot of this I think is fairly common, but putting them together like this is maybe not a combination that most people are familiar with.

Python creates a .tex file, which is then compiled by LaTeX into a PDF, which is split into individual PNG files through GIMP, and then pasted back together into a video using DaVinci Resolve.

1. Python 3.7: I use the [Anaconda](http://www.anaconda.com/) distribution of Python. It's definitely overkill for this, but I also use Python for other stuff and so I'm just used to it.
2. LaTeX: I use the [TeX Live](https://www.tug.org/texlive/) distribution of LaTeX. If you're doing these animations, the browser-based LaTeX services will almost certainly not work well with this. Depending on the complexity of the animation, this can run for quite a long time and produce a lot of pages, and the browser-based services may time out before you're done.
3. [GIMP](https://www.gimp.org/): GIMP is a free program that does image manipulation.
4. [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/): This is a video editing software that I really only barely know how to use, and am not particularly trying to learn to use better.

## Using lanim

I intend to build out a full tutorial at some point in the future. For now, I will give a basic overview of how this thing is supposed to work.

The Lanim class is the basic container that holds all of the information about the animation. The objects that go into class will then influence the final animation. Some of the things are animation objects, such as Circles, Lines, and Nodes. And each of these has rotational attributes that you can use to create the desired animations. You can also put in camera movements. Each of these will be explained in the promised tutorial.

## History

* animate v1 - v5: I went through six and a half versions of making an "animate" module before switching over the lanim name. Those first versions were really just me exploring and implementing different ideas. This is how I eventually came to the use of classes and inheritance as the way to create objects.
* lanim v1: animate v5 went through some fairly substantial revisions, which led me to decide to rename the whole project and start over. This was the version that introduced a lot more of the animation ideas like rotational and transparency attributes, and this is also where I finally was able to implement the camera the way I wanted to.
* Future: I need to learn how to document my stuff in the Python style. This is something that's completely new to me, but it seems like something that would be worth learning. If anything, it should help me to think more clearly about how I approach this project and will potentially help me identify ways to refactor the code to make it more efficient and more functional.
