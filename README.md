# Gamified Education

A website to help gamified courses, built with Django (Python).

Demo is available [here](https://gamified-education.herokuapp.com/). Use "demo" as username and "demodemo" as password. The first page load may take a few seconds.


## Motivation

Life in school is very boring. Teachers usually keep talking on and on while students passively watch them. The main goal is usually getting good grades in tests, instead of practicing the concepts.

But it doesn't have to be like that. There are modern methodologies like [Active Learning](https://en.wikipedia.org/wiki/Active_learning), [Flipped Classroom](https://en.wikipedia.org/wiki/Flipped_classroom), and [Gamification in Learning](https://en.wikipedia.org/wiki/Gamification_of_learning). These concepts can make a huge difference in motivation and performance. I recommend watching [this Extra Credits video](https://www.youtube.com/watch?v=MuDLw1zIc94) and [this TED from Salman Khan](https://www.ted.com/talks/sal_khan_let_s_use_video_to_reinvent_education).

This app targets the Gamification part of the equation.

I give my students an activity (like a small project) in every class. Each activity has many tasks (some are optional), and the students get points when completing them. Then they access this website to see their progress, the class rank, the videos, the links to the theory files, etc.


## Features

  - Login system for students and instructors to access their classes.
  - Invitation by email. All user data is set in admin page, but the students/instructors can create and reset their password.
  - List of activities and tasks, in which students earn XP points. Some of them can be optional and stay hidden until a grade is given.
  - Achievements with automatic rules or manual input.
  - Score ranking, with a customisable size to hide students at the bottom and not upset them.
  - Blog posts (using Markdown).
  - Widgets to display due dates, links, tips, etc (also using Markdown).
  - Responsiveness to small and big screens.
 

## Admin

All data is managed in Django's admin. I've made some customisations to help data input.


## Data Model

I should make a Wiki with all the details, but here is the gist of it:

  - A Course has Assignments (e.g., modules or lessons), Tasks (e.g., exercises) and Badges (medals).
  - A Course has Classes.
  - A Class has Posts and Widgets.
  - A Class associates multiple Assignments with multiple Tasks, giving a XP goal to each combination. This allows each Class to have different grading rules.
  - A Class has Students.
  - A Student gets Grades from each Assignment/Task combination (as a percentage).
  - A Class selects some (or all) Badges from the Course.
  - A Class can have Criteria to each Badge, giving some goal to an Assignment and/or Task.
  - A Student gets Achievements from each Class Badge (as a percentage).
  - A Class has Instructors, which can see the Grades of every Student.
  

## Some of the Dependencies

  - [Django](https://github.com/django/django) (still in version 1)
  - [PostgreSQL](https://www.postgresql.org) (it should be plain SQL, but I use the RANK function)
  - [Django Material](https://github.com/viewflow/django-material)
  - [markdown2](https://github.com/trentm/python-markdown2)
  - [Pygments](https://github.com/pygments/pygments)
  