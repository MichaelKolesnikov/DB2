## Простые запросы:

1. **Сколько вариантов подготовлено для каждого предмета**
```postgresql
select subject.name, count(*) from subject join variant on variant.subject_id=subject.id group by subject.name;
```
2. **Вывести средний балл по каждому предмету для школьника с ID = 1**
```postgresql
SELECT sub.name, AVG(wt.grade) AS average_grade
FROM WrittenTask wt
JOIN WrittenWork ww ON wt.written_work_id = ww.id
JOIN Variant v ON ww.variant_id = v.id
JOIN Subject sub ON v.subject_id = sub.id
WHERE ww.school_child_id = 1
GROUP BY sub.name;
```
3. **Найти все предметы, по которым проводились экзамены в школе с номером 1**
```postgresql
SELECT sub.name
FROM Exam e
JOIN Subject sub on e.subject_id = sub.id
JOIN School s on e.school_id = s.id
WHERE s.name='Школа №1';
```
4. **Вывести топ-10 учителей по количеству проведенных экзаменов.**
```postgresql
SELECT t.id, COUNT(te.exam_id) AS exam_count
FROM Teacher t
JOIN TeacherWithExam te ON t.id = te.teacher_id
GROUP BY t.id
ORDER BY exam_count DESC
LIMIT 10;
```
## Средние запросы:
1. **Для каждого предмета вывести, сколько в нем заданий**
```postgresql
SELECT 
    name, 
    (SELECT COUNT(*) FROM jsonb_object_keys(ScoreMapping_JSON::jsonb)) AS count_of_tasks
FROM subject;
```
2. **Верно ли, что каждый учитель учит в школе, которая находится в том же городе, что и учитель?**
```postgresql
with teacher_city as (
	select teacher.id, school_id, city_id from teacher join address on address.id=teacher.address_id
),
school_city as (
	select school.id as school_id, city_id from school join address on address.id=school.address_id
)
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 
            FROM teacher_city
            JOIN school_city ON teacher_city.school_id = school_city.school_id
            WHERE teacher_city.city_id <> school_city.city_id
        ) THEN 'no'
        ELSE 'yes'
    END AS teacher_city_match
;
```
3. **Какой ребенок какой предмет насколько сдал**
```postgresql
SELECT 
    sc.id,
    s.name AS SubjectName,
    SUM(wt.grade) AS TotalScore
FROM 
    SchoolChild sc
JOIN 
    WrittenWork ww ON sc.id = ww.school_child_id
JOIN 
    WrittenTask wt ON ww.id = wt.written_work_id
JOIN 
    Task t ON wt.task_id = t.id
JOIN 
    Variant v ON ww.variant_id = v.id
JOIN 
    Subject s ON v.subject_id = s.id
GROUP BY 
    sc.id, s.name
ORDER BY 
    sc.id, s.name;
```
4.  **Среднее количество учителей, живущих в одном городе.**
```postgresql
SELECT AVG(teacher_count) AS average_teachers_per_city 
FROM ( 
	SELECT city_id, COUNT(*) AS teacher_count 
	FROM Teacher 
	JOIN Address ON Teacher.address_id = Address.id 
	GROUP BY city_id
) AS city_teacher_counts;
```
## Сложные запросы:
1. **Для каждого учителя сравнить количество его проверенных заданий со средним количеством проверенных заданий одним учителем.**
```postgresql
WITH teacher_tasks AS (
    SELECT 
        teacher_id, 
        COUNT(*) AS tasks_checked
    FROM writtentask
    GROUP BY teacher_id
)
SELECT 
    teacher_id, 
    tasks_checked,
    tasks_checked - AVG(tasks_checked) OVER () AS dif
FROM teacher_tasks
ORDER BY tasks_checked DESC;
```
2. **Найти школьника, который получил самый высокий средний балл по всем предметам, вывести его id, средний балл.**
```postgresql
create temporary table winner as (
	select 0 as id, 0 as average_grade
);
DO $$
DECLARE
    sub_id INTEGER;
    max_grade INTEGER;
    max_school_child_id INTEGER;
BEGIN
    FOR sub_id IN SELECT subject.id FROM subject LOOP
        WITH candidate AS (
            SELECT writtenwork.school_child_id, SUM(writtentask.grade) AS grade 
            FROM writtentask
            JOIN writtenwork ON writtentask.written_work_id = writtenwork.id
            JOIN variant ON writtenwork.variant_id = variant.id
            WHERE variant.subject_id = sub_id
            GROUP BY writtenwork.school_child_id
            ORDER BY grade DESC
            LIMIT 1
        )
        SELECT grade, school_child_id INTO max_grade, max_school_child_id FROM candidate;

        IF max_grade > (SELECT average_grade FROM winner) THEN
            UPDATE winner
            SET id = max_school_child_id, average_grade = max_grade;
        END IF;
    END LOOP;
END $$;
select * from winner;
```
3. **По предмету "Физика" указать средний балл по каждому варианту**
```postgresql
create temporary table physics_id as (
	select subject.id from subject where subject.name='Физика'
);
with marks as (
	select variant.id as var_id, writtenwork.id as work_id, sum(writtentask.grade) as sum_grade
	from writtentask
	join writtenwork
		on writtenwork.id=writtentask.written_work_id
	join variant
		on variant.id=writtenwork.variant_id
	where variant.subject_id=(select physics_id.id from physics_id)
	group by var_id, work_id
)
select marks.var_id, avg(sum_grade) as average
from marks
group by var_id
order by average desc;
```
4. **Вывести средний балл по профильной математике для каждой школы Москвы**
```postgresql
with m_id as (
	select subject.id from subject 
	where subject.name='Математика. Профильный уровень'
),
moscow_id as (
	select city.id from city where city.name='Москва'
)
select marks.school_id, avg(marks.grade) as average from (
select schoolchild.id, schoolchild.school_id, sum(writtentask.grade) as grade from writtentask
	join writtenwork on writtentask.written_work_id=writtenwork.id
	join variant on writtenwork.variant_id=variant.id
	join schoolchild on schoolchild.id=writtenwork.school_child_id
	join address on schoolchild.address_id=address.id
	where variant.subject_id=(select m_id.id from m_id) and address.city_id=(select id from moscow_id)
	group by schoolchild.id
) as marks
group by marks.school_id
order by average desc;
```