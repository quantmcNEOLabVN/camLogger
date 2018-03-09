SELECT 
    'Person with ID=' || p.PERSON_ID || ' appeared in Camera at  ' || to_char(img.TIMERECORDED, 'DD/MM/YYYY  HH24:MI:SS.FF ') as "Reports"
FROM PEOPLE p JOIN EMP_IMG ei ON (p.Person_ID = ei.Person_ID)
    join IMAGES img on (img.Img_ID=ei.Img_ID);
Select * from IMAGES;
Select * from PEOPLE;
select * from EMP_IMG order by IMG_ID ;

SELECT (COUNT(*)+1) FROM EMP_IMG;