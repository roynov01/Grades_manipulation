import tkinter as tk
from matplotlib import pyplot as plt
from tkinter import filedialog as fd
import tkinter.font as fnt
from tkinter import messagebox
import os
from itertools import combinations


CHOICE = 'choice'
GRID_COL = 6
GRID_ROW = 10
EDIT_WINDOW_ROW = 11
EDIT_WINDOW_COL = 4
MIN_GRADE = 60
MAX_GRADE = 100
DEFAULT_TEXT = 'Choice points #'


class Course:
    """class that stores a data of a single course"""
    def __init__(self, id, name: str, points: float, grade: int or str, category: str):
        self.name = name
        self.id = id
        self.grade = grade
        self.points = float(points)
        self.category = category
        try:
            grade = float(grade)
            self.relative_grade = points * grade
            self.is_binary = False
        except ValueError:
            self.is_binary = True
            self.relative_grade = None

    def __str__(self):
        return f'{self.id},{self.name},{self.points},{self.grade},{self.category}'


class Courses:
    """class that if a collection of courses of type Course and their manipulations"""
    def __init__(self):
        self.category_counter = {}
        self.total_points = 0
        self.points_without_binary = 0
        self.total_relative_grades = 0
        self.avg = 0
        self.sd = 0
        self.final_points_amount = None
        self.courses = {}
        self.choice_courses = set()
        self.non_choice_courses = 0

    def set_final_points_amount(self, amount: int):
        self.final_points_amount = amount
        return self.final_points_amount

    def add_course(self, course: Course):
        """adds a course"""
        if not course.is_binary:
            self.courses[course] = False
            self.points_without_binary += course.points
            self.total_relative_grades += course.relative_grade
        else:
            self.courses[course] = True
        if course.category == CHOICE:
            self.choice_courses.add(course.id)
        else:
            self.non_choice_courses += course.points
        if course.category not in self.category_counter:
            self.category_counter[course.category] = course.points
        else:
            self.category_counter[course.category] += course.points
        self.total_points += course.points
        self.update_avg()
        self.update_sd()

    def remove_course(self, course: Course):
        """removes a course"""
        for c in self.courses:
            if course.id == c.id:
                if not self.courses[c]:
                    self.total_relative_grades -= course.relative_grade
                    self.points_without_binary -= course.points
                if course.id in self.choice_courses:
                    self.choice_courses.remove(course.id)
                else:
                    self.non_choice_courses -= course.points
                self.total_points -= course.points
                self.category_counter[course.category] -= course.points
                self.courses.pop(c)
                self.update_avg()
                self.update_sd()
                return

    def update_avg(self):
        """updates the average"""
        try:
            self.avg = self.total_relative_grades / self.points_without_binary
        except ZeroDivisionError:
            return 0

    def update_sd(self):
        """updates the standard deviation"""
        numerator = 0
        for c in self.courses:
            if not self.courses[c]:
                numerator += c.points * ((c.grade - self.avg) ** 2)
        try:
            self.sd = (numerator / self.points_without_binary) ** 0.5
        except ZeroDivisionError:
            return 0

    def __str__(self):
        returned_str = 'id\tpts\tgrade\tname\n'
        if not self.courses:
            return str()
        for c in self.courses:
            returned_str += f'{c.id}\t{str(c.points)}\t{str(c.grade)}\t{c.name}\n'
        return returned_str

    def avg_calc(self, id_lst):
        """calculates the average of a given list of courses (their id)"""
        points_sum, grades_sum = 0, 0
        for id in id_lst:
            for course in self.courses:
                if course.id == id and not self.courses[course]:
                    points_sum += course.points
                    grades_sum += course.relative_grade
        if not points_sum:
            return 0
        return grades_sum/points_sum

    def sum_points(self, id_lst):
        """calculates the sum of points of a given list of courses (their id)"""
        sum_points = 0
        for course in self.courses:
            if course.id in id_lst:
                sum_points += course.points
        return sum_points

    def best_avg(self):
        """creates a list of the best combinations of courses to yield a given amount of points"""
        if not self.final_points_amount:
            return
        results = []
        ids = self.choice_courses
        for i in range(len(ids)):
            results.extend(
                    [(combo, self.avg_calc(combo)) for combo in combinations(ids, i)
                     if self.sum_points(combo) == self.final_points_amount])
        if not results:
            only_combination = tuple([id for id in self.choice_courses])
            results.append((only_combination, self.avg_calc(only_combination)))
            return results
        results.sort(key=lambda z: z[1])
        return list(reversed(results))

    def get_avg(self):
        """returns the standard average"""
        return round(self.avg, 3)

    def get_sd(self):
        """returns the standard deviation"""
        return round(self.sd, 3)

    def copy(self):
        """creates a copy of the object"""
        new_object = Courses()
        for course in self.courses:
            new_object.add_course(course)
        return new_object


class EditWindow:
    """window that handles the editing of data"""
    def __init__(self, root, courses, grades):
        self.courses = courses.copy()
        self.grades_object = grades
        self.courses_original = courses
        self.root = root
        self.root.title("Edit grades")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.iconbitmap('support_files\\pencil.ico')
        self.root.state('zoomed')
        self.root["bg"] = "black"
        self.labels = []
        self.label_id = tk.Label(self.root, text='Course id', font=('Verdana', 14),
                                 anchor='e', width=23, height=2, fg="white", bg='black')
        self.label_name = tk.Label(self.root, text='Name', font=('Verdana', 14),
                                   anchor='e', width=23, height=2, fg="white", bg='black')
        self.label_points = tk.Label(self.root, text='Points amount', font=('Verdana', 14),
                                     anchor='e', width=23, height=2, fg="white", bg='black')
        self.label_grade = tk.Label(self.root, text=f'Grade ({MIN_GRADE}-{MAX_GRADE} or pass)', font=('Verdana', 14),
                                    anchor='e', width=23, height=2, fg="white", bg='black')
        self.label_category = tk.Label(self.root, text='Category', font=('Verdana', 14),
                                       anchor='e', width=23, height=2, fg="white", bg='black')
        self.labels += [self.label_id] + [self.label_name] + [self.label_points] +\
                       [self.label_grade] + [self.label_category]

        self.entries = []
        self.entry_id = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.entry_name = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.entry_points = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.entry_grade = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.entry_category = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.entries += [self.entry_id] + [self.entry_name] + [self.entry_points] +\
                        [self.entry_grade] + [self.entry_category]

        self.button_add = tk.Button(
            self.root, text='Add course', fg='white', bg='purple', width=30, height=4,
            activebackground='blue', relief='raised', command=self.add_course, state='normal', font=fnt.Font(size=20))
        self.label_remove = tk.Label(self.root, text='Course id', font=('Verdana', 14),
                                     anchor='e', width=18, height=2, fg='white', bg='black')
        self.entry_remove = tk.Entry(self.root, cursor='arrow', width=52, bg='gray', bd=3, font=('Verdana', 14))
        self.button_remove = tk.Button(
            self.root, text='Remove course', fg='white', bg='purple', width=30, height=4,
            activebackground='blue', relief='raised', command=self.remove_course, state='normal', font=fnt.Font(size=20))
        self.button_quit = tk.Button(
            self.root, text='Save and quit editing', fg='white', bg='blue', width=30, height=4,
            activebackground='blue', relief='raised', command=self.save_quit, state='normal', font=fnt.Font(size=20))
        self.label_board = tk.Label(self.root, text='', bg="cyan", justify='left', width=80, height=45, )

        index = 0
        for i in range(len(self.entries)):
            self.entries[i].grid(row=index, column=2, padx=5, pady=2)
            self.labels[i].grid(row=index, column=1, padx=5, pady=2)
            index += 1
        self.button_add.grid(row=5, column=2, padx=5, pady=2, columnspan=1)
        self.label_remove.grid(row=6, column=1, padx=5, pady=2)
        self.entry_remove.grid(row=6, column=2, padx=5, pady=2)
        self.button_remove.grid(row=7, column=2, padx=5, pady=2, columnspan=1)
        self.button_quit.grid(row=7, column=3, padx=5, pady=2)
        self.label_board.grid(row=0, column=3, padx=5, pady=2, rowspan=7)
        self.update_board()

    def quit(self):
        """quits the editing window"""
        if not messagebox.askokcancel("Quit", "Quit without saving?"):
            self.grades_object.cont()
            self.root.destroy()

    def update_board(self):
        self.label_board['text'] = str(self.courses)

    def add_course(self):
        """add a new course"""
        self.entry_remove['bg'] = 'gray'
        course_data = []
        for entry in self.entries:
            entry.configure(bg='gray')
            course_data.append(self.check_entry(entry))
        if all(course_data):
            duplicate = None
            for course in self.courses.courses:
                if course.id == course_data[0]:
                    duplicate = course
            if duplicate:
                self.courses.remove_course(duplicate)
            self.courses.add_course(Course(*course_data))
            for entry in self.entries:
                entry.delete(0, 'end')
            self.update_board()

    def check_entry(self, entry):
        """check that the entry is filled with the appropriate data"""
        if not entry.get():
            entry.configure(bg='pink')
            return
        if entry is self.entry_grade:
            if entry.get() == 'pass':
                return entry.get()
            try:
                grade = float(entry.get())
                if grade < MIN_GRADE or grade > MAX_GRADE:
                    entry.configure(bg='pink')
                    return
                else:
                    return grade
            except ValueError:
                entry.configure(bg='pink')
                return
        if entry is self.entry_points:
            try:
                points = float(entry.get())
                if points > 0:
                    return points
                entry.configure(bg='pink')
                return
            except ValueError:
                entry.configure(bg='pink')
                return
        return entry.get()

    def remove_course(self):
        """remove an existing course"""
        self.entry_remove['bg'] = 'gray'
        for entry in self.entries:
            entry.configure(bg='gray')
        self.entry_remove.configure(bg='gray')
        entry_input = self.entry_remove.get()
        if not entry_input:
            self.entry_remove.configure(bg='pink')
            return
        for course in self.courses.courses:
            if entry_input == course.id:
                self.courses.remove_course(course)
                self.entry_remove.delete(0, 'end')
                self.update_board()
                return
        self.entry_remove.configure(bg='pink')

    def save_quit(self):
        """transfers the edited grades to the main window and quits the editing window"""
        if messagebox.askyesno("Quit", "Do you wish to save and quit?"):
            self.courses_original.courses = self.courses.courses
            self.grades_object.cont()
            self.root.destroy()


class Grades:
    """main class of the program"""
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('support_files\\pencil.ico')
        self.root.state('zoomed')
        root.protocol("WM_DELETE_WINDOW", self.quit_attempt)
        self.name = ''
        self.best_avg_iter = None
        self.best_avg_list = None
        self.current_chart = None
        self.filename = None
        self.saved = True
        self.courses = Courses()

        # widgets:
        self.open_file_button = tk.Button(
            self.root, text='open grades file', fg='black', bg='lightblue', width=20, height=4,
            activebackground='blue', relief='raised', command=self.open_file, state='normal', font=fnt.Font(size=20)
        )
        self.new_file_button = tk.Button(
            self.root, text='create new grades file', fg='black', bg='lightblue', width=20, height=4, relief='raised',
            activebackground='blue', command=self.new_grades_file, state='normal', font=fnt.Font(size=20)
        )
        self.edit_button = tk.Button(
            self.root, text='edit grades', fg='black', bg='lightblue', width=20, height=4,
            activebackground='blue', relief='raised', command=self.edit_grades, state='normal', font=fnt.Font(size=20)
        )
        self.save_grades_button = tk.Button(
            self.root, text='save changes', fg='black', bg='lightblue', width=20, height=4,
            activebackground='blue', relief='raised', command=self.save_grades, state='normal', font=fnt.Font(size=20)
        )
        self.board_label = tk.Label(self.root, text='', bg='khaki1',
                                    justify='left', width=70, height=52, relief='groove')

        self.entry = tk.Entry(self.root, cursor='xterm', width=13, bg='white', bd=5, font=('Verdana', 25))
        self.entry.insert(-1, DEFAULT_TEXT)

        self.plot_button = tk.Button(
            self.root, text='plot\ngrades per course', fg='black', bg='DeepSkyBlue2', width=20, height=2,
            activebackground='blue', relief='raised', command=self.plot_grades, state='normal', font=fnt.Font(size=20)
        )
        self.histogram_button = tk.Button(
            self.root, text='plot\ngrades histogram', fg='black', bg='DeepSkyBlue2', width=20, height=2,
            activebackground='blue', relief='raised', command=self.histogram, state='normal', font=fnt.Font(size=20)
        )
        self.piechart_button = tk.Button(
            self.root, text='plot\ncourse categories', fg='black', bg='DeepSkyBlue2', width=20, height=2,
            activebackground='blue', relief='raised', command=self.piechart, state='normal', font=fnt.Font(size=20)
        )
        self.show_characteristics_button = tk.Button(
            self.root, text='show overall\ncharacteristics', fg='black', bg='wheat4', width=20, height=2, state='normal',
            activebackground='blue', relief='raised', command=self.show_characteristics, font=fnt.Font(size=20)
        )
        self.characteristics_label = tk.Label(
            self.root, text='', bg='LightYellow3', justify='left', width=27, height=8, relief='groove',
            font=fnt.Font(size=16))
        self.best_avg_button = tk.Button(
            self.root, text='calculate best average', fg='black', bg='SeaGreen1', width=20, height=2,
            activebackground='blue', relief='raised', command=self.best_avg, state='normal', font=fnt.Font(size=20)
        )
        self.next_button = tk.Button(
            self.root, text='next', fg='black', bg='SeaGreen1', width=20, height=2, font=fnt.Font(size=20),
            activebackground='blue', relief='raised', command=self.update_best_avg_label, state='normal'
        )
        self.best_avg_label = tk.Label(self.root, text='', bg='aquamarine2',
                                       justify='left', width=46, height=28, relief='groove')
        self.save_best_options_button = tk.Button(
            self.root, text='save best options', fg='black', bg='SeaGreen1', width=20, height=2, font=fnt.Font(size=20),
            activebackground='blue', relief='raised', command=self.save_best_options, state='normal'
        )

        # functional placements:
        self.open_file_button.grid(column=1, row=1, rowspan=2, padx=5, pady=1)
        self.new_file_button.grid(column=1, row=3, rowspan=2, padx=5, pady=1)
        self.edit_button.grid(column=1, row=5, rowspan=2, padx=5, pady=1)
        self.save_grades_button.grid(column=1, row=7, rowspan=2, padx=5, pady=1)
        self.board_label.grid(column=2, row=1, rowspan=8, padx=5, pady=1)
        self.entry.grid(column=3, row=1, rowspan=1, padx=5, pady=1)
        self.plot_button.grid(column=3, row=2, rowspan=1, padx=5, pady=1)
        self.histogram_button.grid(column=3, row=3, rowspan=1, padx=5, pady=1)
        self.piechart_button.grid(column=3, row=4, rowspan=1, padx=5, pady=1)
        self.show_characteristics_button.grid(column=3, row=5, rowspan=1, padx=5, pady=1)
        self.characteristics_label.grid(column=3, row=6, rowspan=3, padx=5, pady=1)
        self.best_avg_button.grid(column=4, row=1, rowspan=1, padx=5, pady=1)
        self.next_button.grid(column=4, row=2, rowspan=1, padx=5, pady=1)
        self.best_avg_label.grid(column=4, row=3, rowspan=5, padx=5, pady=1)
        self.save_best_options_button.grid(column=4, row=8, rowspan=1, padx=5, pady=1)

        self.update_state()  # disabling the relevant buttons

    def update_state(self):
        """updates which buttons are disabled and window title"""
        self.root.title(f'Grades manipulator')
        if self.filename:
            name = self.filename.split('/')[-1]
            name = name[:-4]  # deletes the ".csv"
            self.root.title(f'Grades manipulator - {name}')
            self.name = name
        for widget in [self.open_file_button, self.entry, self.new_file_button, self.save_grades_button,
                       self.show_characteristics_button, self.next_button, self.best_avg_button]:
            widget.configure(state='normal')
        if self.best_avg_label['text']:
            self.save_best_options_button.configure(state='normal')
        self.edit_button.configure(state='normal') if self.filename else self.edit_button.configure(state='disabled')
        if not self.courses.courses:
            for widget in [self.plot_button, self.save_best_options_button, self.histogram_button, self.piechart_button]:
                widget.configure(state='disabled')
        else:
            for widget in [self.plot_button, self.save_best_options_button, self.histogram_button, self.piechart_button,
                           self.edit_button]:
                widget.configure(state='normal')

    def open_file(self):
        """opens a CSV file"""
        while True:
            filename = fd.askopenfilename(filetypes=[("CSV file", "*.csv")],
                                          initialdir=os.path.abspath(os.getcwd())+'\\files')
            if not filename:
                return
            if filename.endswith('.csv'):
                break
        self.filename = filename
        with open(filename, 'r') as file:
            for line in file:
                attributes = line.strip().split(',')  # id, name, points, grade, category
                attributes[2] = float(attributes[2])
                try:
                    attributes[3] = float(attributes[3])
                except ValueError:
                    pass
                course = Course(*attributes)
                self.courses.add_course(course)
        self.saved = True
        self.characteristics_label['text'] = ''
        self.best_avg_label['text'] = ''
        self.update_board()
        self.update_state()

    def update_board(self):
        """updates the board_label (courses table)"""
        self.board_label['text'] = str(self.courses)

    def edit_grades(self):
        """opens new window with editing options (remove or add courses)"""
        self.saved = False
        edit_win = tk.Toplevel(self.root)
        EditWindow(edit_win, self.courses, self)
        self.disable_all()

    def disable_all(self):
        """disables all buttons and entries"""
        widgets = [self.best_avg_button, self.plot_button, self.next_button, self.edit_button, self.piechart_button,
                   self.save_grades_button, self.open_file_button, self.new_file_button, self.histogram_button,
                   self.show_characteristics_button, self.save_best_options_button, self.entry]
        for widget in widgets:
            widget.configure(state='disabled')

    def cont(self):
        """handles the isntance in which the user saved and closed the editing window"""
        self.update_state()
        self.update_board()

    def new_grades_file(self):
        """creates a new CSV file"""
        if not self.saved:
            if not messagebox.askokcancel("New file", "Create new file?\nPrevious file will not be saved!"):
                return
        filename = fd.asksaveasfilename(
            filetypes=[("CSV file", "*.csv")], defaultextension='.csv',
            initialdir=os.path.abspath(os.getcwd()) + '\\files', title="Choose filename")
        if not filename:
            return
        if not filename.endswith('.csv'):
            filename += '.csv'
        self.saved = True
        self.filename = filename
        self.characteristics_label['text'] = ''
        self.best_avg_label['text'] = ''
        self.courses = Courses()
        self.update_board()
        self.update_state()

    def save_grades(self):
        """writes the current data to the opened file"""
        if not self.courses.courses:
            return
        if not self.saved:
            courses_str = [str(course) for course in self.courses.courses]
            with open(self.filename, 'w') as file:
                file.write('\n'.join(courses_str))
            self.saved = True
            messagebox.showinfo(title='', message='File has been saved')

    def plot_grades(self):
        """creates a bar-plot of the grades"""
        plt.close('all')
        data = []
        for course in self.courses.courses:
            if not self.courses.courses[course]:  # not binary grade
                data.append((course.name, course.grade))
        data.sort(key=lambda z: z[1])
        names, grades = [], []
        for i in data:
            names.append(i[0])
            grades.append(i[1])
        if names:
            plt.barh(names, grades)
            plt.title("Courses Grades")
            plt.xlabel("grade")
            mng = plt.get_current_fig_manager()
            mng.set_window_title('Courses by grade bar-plot')
            mng.window.state('zoomed')
            mng.window.wm_iconbitmap("support_files\\barplot.ico")
            plt.subplots_adjust(left=0.33, top=0.93, right=0.9)
            plt.show()

    def histogram(self):
        """creates a histogram of the grades"""
        plt.close('all')
        grades, points = [], []
        for course in self.courses.courses:
            if not self.courses.courses[course]:  # not binary grade
                grades.append(course.grade)
                points.append(course.points)
        bins = list(range(10, 101, 5))  # [10, 15, 20, ... , 95, 100]
        if grades:
            plt.hist(grades, weights=points, bins=bins, edgecolor="black", color="lightgreen", log=False)
            plt.title("Grades Histogram")
            plt.xlabel("grade")
            plt.ylabel("points")
            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed')
            mng.set_window_title('Grades histogram')
            mng.window.wm_iconbitmap("support_files\\histogram.ico")
            plt.tight_layout()  # adjust plot spacing
            plt.show()

    def piechart(self):
        """creates a pie-chart of the courses categories"""
        plt.close('all')
        categories, count = [], []
        colors = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', 'mediumorchid', 'chocolate', 'grey', 'aqua']
        categories = self.courses.category_counter.keys()
        count = self.courses.category_counter.values()
        if categories:
            plt.pie(count, labels=categories, wedgeprops={'edgecolor': 'black'}, colors=colors, shadow=True,
                    startangle=90, autopct=lambda p: f'{p * sum(count) / 100 :.0f}')
            plt.title("Courses Categories")
            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed')
            mng.set_window_title('Course categories pie-chart')
            mng.window.wm_iconbitmap("support_files\\pie_chart.ico")
            plt.tight_layout()  # adjust plot spacing
            plt.show()

    def show_characteristics(self):
        """displays general characteristics of the grades and points (avg, sd...)"""
        self.characteristics_label['text'] = ''
        self.characteristics_label['text'] += \
            f'Total points:\t{self.courses.total_points}\nWithout " choice ":\t{self.courses.non_choice_courses}\n' \
            f'Average:\t\t{self.courses.get_avg()}\nSD:\t\t{self.courses.get_sd()}'

    def best_avg(self):
        """creates an iterator that contains the best choices for the highest average based on amount of points in
        the entry"""
        self.best_avg_label['text'] = ''
        amount = self.entry.get()
        try:
            amount = int(amount)
            self.entry.configure(bg='white')
        except ValueError:
            self.entry.configure(bg='pink')
            return
        self.courses.set_final_points_amount(amount)
        self.best_avg_list = self.courses.best_avg()
        self.best_avg_iter = iter(self.best_avg_list)
        self.update_best_avg_label()

    def update_best_avg_label(self):
        """shows the next best choice of highest average"""
        label = str()
        try:
            courses, avg = next(self.best_avg_iter)
            avg = round(avg, 3)
            for course in self.courses.courses:
                for id in courses:
                    if course.id == id:
                        label += f'- {course.name}\n'
            if avg:
                label += f'average: {avg}\n\n'
            self.best_avg_label['text'] += label
        except StopIteration:
            pass
        self.save_best_options_button.configure(state='normal')

    def save_best_options(self):
        """saves the best combinations of courses with the highest average to a txt file"""
        if not self.courses.courses:
            return
        with open(f'files\\{self.name}_best_options.txt', 'w') as file:
            for courses, avg in self.best_avg_list:
                file.write(str(avg) + ': ')
                for id in courses:
                    for course in self.courses.courses:
                        if course.id == id:
                            file.write(course.name)
                            if id != courses[-1]:
                                file.write(', ')
                file.write('\n')

    def quit_attempt(self):
        """handles the closing of the program"""
        if not self.saved:
            if messagebox.askokcancel("Quit", "Quit without saving?"):
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    Grades(window)
    window.mainloop()
