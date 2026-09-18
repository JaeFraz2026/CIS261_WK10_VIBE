#Jaquan Frazier
#CIS261
#WK10 VIBE Coding

"""Student record manager with test-score and letter-grade calculations."""

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path


DATA_FILE = Path("student_grades.txt")


class ExitProgram(Exception):
	"""Signal that the user pressed ESC during an input prompt."""


@dataclass
class Student:
	"""Store one student's identifying information and test scores."""

	student_id: str
	name: str
	test_1: float
	test_2: float
	test_3: float
	average: float = field(init=False)
	grade: str = field(init=False)

	def __post_init__(self) -> None:
		"""Calculate the average and letter grade after creating the student."""
		self.average = (self.test_1 + self.test_2 + self.test_3) / 3
		if self.average >= 90:
			self.grade = "A"
		elif self.average >= 80:
			self.grade = "B"
		elif self.average >= 70:
			self.grade = "C"
		elif self.average >= 60:
			self.grade = "D"
		else:
			self.grade = "F"


class StudentManager:
	"""Manage student records by their unique student IDs."""

	def __init__(self) -> None:
		self.records: dict[str, Student] = {}

	def add_student(
		self,
		student_id: str,
		name: str,
		test_1: float,
		test_2: float,
		test_3: float,
	) -> Student:
		"""Add a student with three validated test scores."""
		student_id = student_id.strip()
		name = name.strip()
		if not student_id or not name:
			raise ValueError("Student ID and name are required.")
		if student_id in self.records:
			raise ValueError("A student with that ID already exists.")
		for score in (test_1, test_2, test_3):
			if not 0 <= score <= 100:
				raise ValueError("Scores must be between 0 and 100.")

		record = Student(student_id, name, test_1, test_2, test_3)
		self.records[student_id] = record
		return record

	def get_student(self, student_id: str) -> Student:
		"""Return a student record or raise a clear error when it is missing."""
		try:
			return self.records[student_id.strip()]
		except KeyError as error:
			raise ValueError("Student ID not found.") from error

	def all_students(self) -> list[Student]:
		"""Return records sorted by student ID for consistent display."""
		return [self.records[key] for key in sorted(self.records)]

	def search_by_name(self, name: str) -> list[Student]:
		"""Find students whose names contain the search text, ignoring case."""
		search_text = name.strip().casefold()
		return [
			record
			for record in self.all_students()
			if search_text in record.name.casefold()
		]

	def save(self, file_path: Path = DATA_FILE) -> None:
		"""Save records as name|id|test1|test2|test3|average|grade."""
		with file_path.open("w", newline="", encoding="utf-8") as file:
			for record in self.all_students():
				file.write(
					f"{record.name}|{record.student_id}|{record.test_1:.2f}|"
					f"{record.test_2:.2f}|{record.test_3:.2f}|"
					f"{record.average:.2f}|{record.grade}\n"
				)

	@classmethod
	def load(cls, file_path: Path = DATA_FILE) -> "StudentManager":
		"""Load records from disk, returning an empty manager if none exist."""
		manager = cls()
		if not file_path.exists():
			return manager

		with file_path.open(newline="", encoding="utf-8") as file:
			reader = csv.reader(file, delimiter="|")
			for row in reader:
				if not row:
					continue
				try:
					if len(row) != 7:
						raise ValueError("Each record must contain seven fields.")
					manager.add_student(
						row[1],
						row[0],
						float(row[2]),
						float(row[3]),
						float(row[4]),
					)
					float(row[5])
					if row[6] not in {"A", "B", "C", "D", "F"}:
						raise ValueError("Invalid letter grade.")
				except (KeyError, TypeError, ValueError) as error:
					raise ValueError("The student records file contains invalid data.") from error
		return manager

	def statistics(self) -> tuple[Student, Student, float] | None:
		"""Return the highest record, lowest record, and class average."""
		students = self.all_students()
		if not students:
			return None
		highest = max(students, key=lambda record: record.average)
		lowest = min(students, key=lambda record: record.average)
		class_average = sum(record.average for record in students) / len(students)
		return highest, lowest, class_average


def display_table(records: list[Student]) -> None:
	"""Print student records in a formatted table."""
	if not records:
		print("No student records found.")
		return
	header = f"{'ID':<12} {'Name':<24} {'Test 1':>8} {'Test 2':>8} {'Test 3':>8} {'Average':>9} {'Grade':>5}"
	print(header)
	print("-" * len(header))
	for record in records:
		print(
			f"{record.student_id:<12} {record.name:<24.24} "
			f"{record.test_1:>8.2f} {record.test_2:>8.2f} "
			f"{record.test_3:>8.2f} {record.average:>9.2f} {record.grade:>5}"
		)


def save_records(manager: StudentManager) -> bool:
	"""Save records and report file-operation errors clearly."""
	try:
		manager.save()
	except OSError as error:
		print(f"Unable to save records to {DATA_FILE}: {error}")
		return False
	print(f"Student records saved to {DATA_FILE}.")
	return True


def input_with_escape(prompt: str) -> str:
	"""Read a line, exiting immediately when ESC is pressed in a terminal."""
	if not sys.stdin.isatty() or sys.platform == "win32":
		value = input(prompt)
		if "\x1b" in value:
			raise ExitProgram
		return value

	import termios
	import tty

	print(prompt, end="", flush=True)
	characters: list[str] = []
	file_descriptor = sys.stdin.fileno()
	previous_settings = termios.tcgetattr(file_descriptor)
	try:
		tty.setcbreak(file_descriptor)
		while True:
			character = sys.stdin.read(1)
			if character == "\x1b":
				print()
				raise ExitProgram
			if character in "\r\n":
				print()
				return "".join(characters)
			if character in "\b\x7f":
				if characters:
					characters.pop()
					print("\b \b", end="", flush=True)
				continue
			characters.append(character)
			print(character, end="", flush=True)
	finally:
		termios.tcsetattr(file_descriptor, termios.TCSADRAIN, previous_settings)


def prompt_for_score(test_name: str) -> float:
	"""Read and validate a score from the user."""
	while True:
		try:
			score = float(input_with_escape(f"{test_name} score (0-100): "))
		except ValueError:
			print("Please enter a number from 0 to 100.")
			continue
		if 0 <= score <= 100:
			return score
		print("Please enter a number from 0 to 100.")


def show_menu() -> None:
	"""Display the available application commands."""
	print(
		"\nStudent Record Manager\n"
		"1. Add student record\n"
		"2. Display all students\n"
		"3. Class statistics\n"
		"4. Search by student name\n"
		"5. Exit (or press ESC)"
	)


def run() -> None:
	"""Run the interactive student record manager."""
	try:
		manager = StudentManager.load()
	except (OSError, ValueError) as error:
		print(f"Could not load {DATA_FILE}: {error}")
		manager = StudentManager()
	if manager.records:
		print(f"Loaded {len(manager.records)} student record(s).")

	while True:
		show_menu()

		try:
			choice = input_with_escape("Choose an option: ").strip()
			if choice == "1":
				student_id = input_with_escape("Student ID: ")
				name = input_with_escape("Student name: ")
				test_1 = prompt_for_score("Test 1")
				test_2 = prompt_for_score("Test 2")
				test_3 = prompt_for_score("Test 3")
				manager.add_student(student_id, name, test_1, test_2, test_3)
				print("Student added successfully. You may add another student.")
				save_records(manager)
			elif choice == "2":
				display_table(manager.all_students())
			elif choice == "3":
				result = manager.statistics()
				if result is None:
					print("No student records found.")
				else:
					highest, lowest, class_average = result
					print(f"Highest average: {highest.name} ({highest.average:.2f})")
					print(f"Lowest average: {lowest.name} ({lowest.average:.2f})")
					print(f"Class average: {class_average:.2f}")
			elif choice == "4":
				matches = manager.search_by_name(input_with_escape("Search name: "))
				display_table(matches)
			elif choice == "5":
				save_records(manager)
				print("Goodbye.")
				return
			else:
				print("Please choose an option from 1 to 5.")
		except ExitProgram:
			save_records(manager)
			print("Goodbye.")
			return
		except (EOFError, KeyboardInterrupt):
			print()
			save_records(manager)
			print("Goodbye.")
			return
		except ValueError as error:
			print(f"Error: {error}")


if __name__ == "__main__":
	run()
